import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, 
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import json
import os
import re
from loguru import logger

class QwenTimeSeriesModel:
    """基于Qwen的时间序列预测模型"""
    
    def __init__(self, model_name: str = "Qwen/Qwen2.5-7B-Instruct", 
                 max_length: int = 512, device: str = "auto"):
        self.model_name = model_name
        self.max_length = max_length
        self.device = torch.device("cuda" if torch.cuda.is_available() and device == "auto" else device)
        
        self.tokenizer = None
        self.model = None
        self.is_trained = False
        
        logger.info(f"初始化QwenTimeSeriesModel，设备: {self.device}")
    
    def load_model(self, model_path: Optional[str] = None):
        """加载预训练模型"""
        try:
            model_path = model_path or self.model_name
            
            logger.info(f"加载模型: {model_path}")
            
            # 加载分词器
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                padding_side="right"
            )
            
            # 设置pad_token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            logger.info("模型加载成功")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def prepare_lora_model(self, r: int = 8, alpha: int = 32, dropout: float = 0.1):
        """准备LoRA微调模型"""
        if self.model is None:
            raise ValueError("请先加载基础模型")
        
        # LoRA配置
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=r,
            lora_alpha=alpha,
            lora_dropout=dropout,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            bias="none",
        )
        
        # 应用LoRA
        self.model = get_peft_model(self.model, lora_config)
        self.model.print_trainable_parameters()
        
        logger.info("LoRA模型准备完成")
    
    def format_time_series_prompt(self, series: List[float], task_type: str = "weather") -> str:
        """将时间序列数据格式化为自然语言提示"""
        
        # 将数值转换为字符串，按位分解
        formatted_values = []
        for val in series:
            # 将数字按位分解，例如 12.34 -> "1 2 . 3 4"
            val_str = f"{val:.4f}".rstrip('0').rstrip('.')
            formatted_val = ' '.join(list(val_str))
            formatted_values.append(formatted_val)
        
        # 根据任务类型生成提示词
        if task_type == "weather":
            prompt = f"根据过去{len(series)}个时间点的天气数据：{', '.join(formatted_values)}，请预测下一个时间点的数值。只输出数字，格式与输入相同："
        elif task_type == "electricity":
            prompt = f"根据过去{len(series)}个时间点的电力负荷数据：{', '.join(formatted_values)}，请预测下一个时间点的用电量。只输出数字，格式与输入相同："
        elif task_type == "traffic":
            prompt = f"根据过去{len(series)}个时间点的交通流量数据：{', '.join(formatted_values)}，请预测下一个时间点的流量。只输出数字，格式与输入相同："
        else:
            prompt = f"根据过去{len(series)}个时间点的数据：{', '.join(formatted_values)}，请预测下一个时间点的数值。只输出数字，格式与输入相同："
        
        return prompt
    
    def parse_prediction(self, generated_text: str) -> float:
        """解析模型生成的预测结果"""
        try:
            # 提取生成文本中的数字部分
            # 找到最后一个冒号后的内容
            if "：" in generated_text:
                prediction_part = generated_text.split("：")[-1].strip()
            elif ":" in generated_text:
                prediction_part = generated_text.split(":")[-1].strip()
            else:
                prediction_part = generated_text.strip()
            
            # 移除空格并重新组合数字
            cleaned = prediction_part.replace(" ", "")
            
            # 使用正则表达式提取数字
            numbers = re.findall(r'-?\d+\.?\d*', cleaned)
            if numbers:
                return float(numbers[0])
            else:
                logger.warning(f"无法解析预测结果: {generated_text}")
                return 0.0
                
        except Exception as e:
            logger.error(f"解析预测结果失败: {e}, 原文: {generated_text}")
            return 0.0
    
    def create_training_data(self, data: pd.DataFrame, sequence_length: int = 10, 
                           task_type: str = "weather") -> List[Dict]:
        """创建训练数据"""
        training_data = []
        
        # 假设数据的第一列是时间序列值
        values = data.iloc[:, 0].values
        
        for i in range(len(values) - sequence_length):
            input_sequence = values[i:i+sequence_length].tolist()
            target_value = values[i+sequence_length]
            
            # 生成提示词
            prompt = self.format_time_series_prompt(input_sequence, task_type)
            
            # 格式化目标值
            target_str = f"{target_value:.4f}".rstrip('0').rstrip('.')
            target_formatted = ' '.join(list(target_str))
            
            # 构造完整的训练文本
            full_text = prompt + target_formatted
            
            training_data.append({
                'input_text': prompt,
                'target_text': target_formatted,
                'full_text': full_text
            })
        
        logger.info(f"创建了 {len(training_data)} 个训练样本")
        return training_data
    
    def train(self, training_data: List[Dict], output_dir: str, 
              num_epochs: int = 3, learning_rate: float = 5e-5,
              batch_size: int = 4, gradient_accumulation_steps: int = 4):
        """训练模型"""
        
        if self.model is None:
            raise ValueError("请先加载模型")
        
        # 准备数据集
        def tokenize_function(examples):
            model_inputs = self.tokenizer(
                examples['full_text'],
                truncation=True,
                padding=True,
                max_length=self.max_length,
                return_tensors="pt"
            )
            model_inputs["labels"] = model_inputs["input_ids"].clone()
            return model_inputs
        
        # 转换为datasets格式
        from datasets import Dataset
        train_texts = [item['full_text'] for item in training_data]
        train_dataset = Dataset.from_dict({'full_text': train_texts})
        train_dataset = train_dataset.map(tokenize_function, batched=True)
        
        # 训练参数
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            learning_rate=learning_rate,
            warmup_steps=100,
            logging_steps=10,
            save_steps=500,
            save_total_limit=2,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
            fp16=torch.cuda.is_available(),
        )
        
        # 数据整理器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
            pad_to_multiple_of=8
        )
        
        # 训练器
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
        )
        
        logger.info("开始训练...")
        trainer.train()
        
        # 保存模型
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        self.is_trained = True
        logger.info(f"训练完成，模型保存至: {output_dir}")
    
    def predict_single(self, input_sequence: List[float], task_type: str = "weather") -> float:
        """单次预测"""
        if self.model is None:
            raise ValueError("请先加载模型")
        
        # 生成提示词
        prompt = self.format_time_series_prompt(input_sequence, task_type)
        
        # 编码输入
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_length
        ).to(self.device)
        
        # 生成预测
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.1,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # 解码输出
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 解析预测结果
        prediction = self.parse_prediction(generated_text)
        
        return prediction
    
    def predict_batch(self, sequences: List[List[float]], task_type: str = "weather") -> List[float]:
        """批量预测"""
        predictions = []
        for seq in sequences:
            pred = self.predict_single(seq, task_type)
            predictions.append(pred)
        return predictions
    
    def save_model(self, save_path: str):
        """保存模型"""
        if self.model is None:
            raise ValueError("没有可保存的模型")
        
        os.makedirs(save_path, exist_ok=True)
        
        # 保存模型和分词器
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        
        # 保存配置信息
        config = {
            'model_name': self.model_name,
            'max_length': self.max_length,
            'is_trained': self.is_trained
        }
        
        with open(os.path.join(save_path, 'model_config.json'), 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"模型已保存至: {save_path}")
    
    def load_trained_model(self, model_path: str):
        """加载已训练的模型"""
        try:
            # 加载配置
            config_path = os.path.join(model_path, 'model_config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.max_length = config.get('max_length', self.max_length)
                self.is_trained = config.get('is_trained', False)
            
            # 加载模型
            self.load_model(model_path)
            
            logger.info(f"已训练模型加载成功: {model_path}")
            
        except Exception as e:
            logger.error(f"加载已训练模型失败: {e}")
            raise
