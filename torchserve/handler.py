from ts.torch_handler.base_handler import BaseHandler
from ts.metrics.metric_type_enum import MetricTypes
from ts.utils.util import PredictionException
import torch
import json
from model import SimpleModel
import logging
import os

class SimpleHandler(BaseHandler):
    def __init__(self):
        super(SimpleHandler, self).__init__()
        self.model = SimpleModel()
        #custom metrics
        self.count = 0
        self.mean = {}
        self.var = {}
    
    def initialize(self, context):
        """
        Invoke by torchserve for loading a model
        :param context: context contains model server system properties
        :return:
        """        
        super().initialize(context)
        self.context = context
        metrics = context.metrics
        if os.path.exists('model_config.json'):
            with open('model_config.json', 'r') as config_file:
                config = json.load(config_file)
                self.input_dim = config.get('input_dim', 2)
        else:
            logging.warn('model_config.json file not found')
            self.input_dim = 2

        self.model.load_state_dict(torch.load("model.pth", map_location=torch.device('cpu')))
        self.model.eval()

        # metrics
        self.invalid_input_count = metrics.add_metric_to_cache(
            metric_name="invalid_input_count", 
            unit="count", 
            dimension_names=[], 
            metric_type=MetricTypes.COUNTER
        )
        for i in range(1, self.input_dim + 1):
            self.mean[f'x{i}'] = 0.0
            self.var[f'x{i}'] = 0.0

        for i in range(1, self.input_dim + 1):

            metrics.add_metric_to_cache(
                metric_name=f"input_mean_x{i}", 
                unit="value", 
                dimension_names=["ModelName"], 
                metric_type=MetricTypes.GAUGE 
            )
            
            metrics.add_metric_to_cache(
                metric_name=f"input_var_x{i}", 
                unit="value", 
                dimension_names=["ModelName"], 
                metric_type=MetricTypes.GAUGE
            )

        # self.input_mean_x2 = metrics.add_metric_to_cache(
        #     metric_name="input_mean_x2", 
        #     unit="value", 
        #     dimension_names=["ModelName"], 
        #     metric_type=MetricTypes.GAUGE 
        # )
        
        # self.input_var_x2 = metrics.add_metric_to_cache(
        #     metric_name="input_var_x2", 
        #     unit="value", 
        #     dimension_names=["ModelName"], 
        #     metric_type=MetricTypes.GAUGE
        # )        


    def preprocess(self, data):
        """
        Function to prepare data from the model
        
        :param requests:
        :return: tensor of the processed shape specified by the model
        """
        #data processing
        preprocessed_data = data[0].get("data",None)
        if preprocessed_data is None:
            preprocessed_data = data[0]['body']['data']


        if len(preprocessed_data) != self.input_dim:
            self.invalid_input_count.add_or_update(value=1, dimension_values=[])
            raise PredictionException(f"Invalid input dimensions. Expected {self.input_dim} but got {len(preprocessed_data)}.", 513) 
        preprocessed_data = torch.tensor(preprocessed_data).float()
        #metrics processing
        self.update_input_metrics(preprocessed_data)

        return preprocessed_data

    def inference(self, input_tensor):
        """
        Given the data from .preprocess, perform inference using the model.
        :param requests:
        :return: tensor of the processed shape specified by the model
        """               
        with torch.no_grad():
            output = self.model(input_tensor)
        
        return output

    def postprocess(self, inference_output):
        
        postprocess_output = [{"output": inference_output.item()}]
    
        return postprocess_output

    def handle(self, data, context):
        """
        Invoke by TorchServe for prediction request.
        Do pre-processing of data, prediction using model and postprocessing of prediciton output
        :param data: Input data for prediction
        :param context: Initial context contains model server system properties.
        :return: prediction output
        """
        
        model_input = self.preprocess(data)
        model_output = self.inference(model_input)
        return self.postprocess(model_output)
    

    def update_input_metrics(self, preprocessed_data):
        """
        Update mean and variance incrementally using Welford's method.
        """
        self.count += 1
        for i, value in enumerate(preprocessed_data):
            i += 1 #index offset by 1
            delta = value - self.mean[f'x{i}']
            self.mean[f'x{i}'] += delta / self.count
            self.var[f'x{i}'] += delta * (value - self.mean[f'x{i}'])
            
            self.context.metrics.get_metric(metric_name=f'input_mean_x{i}', metric_type=MetricTypes.GAUGE).\
                add_or_update(value=self.mean[f'x{i}'], dimension_values=[self.context.model_name])
            self.context.metrics.get_metric(metric_name=f'input_var_x{i}', metric_type=MetricTypes.GAUGE).\
                add_or_update(value=self.var[f'x{i}'] / (self.count - 1) if self.count > 0 else 0, dimension_values=[self.context.model_name])


        # x1, x2 = preprocessed_data

        # self.count += 1

        # x1_delta = x1 - self.mean_x1
        # x2_delta = x2 - self.mean_x2

        # self.mean_x1 += x1_delta / (self.count)
        # self.mean_x2 += x2_delta / (self.count)
        
        # self.var_x1 += x1_delta * (x1 - self.mean_x1)
        # self.var_x2 += x2_delta * (x2 - self.mean_x2)

        # self.input_mean_x1.add_or_update(value=self.mean_x1, dimension_values=[self.context.model_name])
        # self.input_var_x1.add_or_update(value=self.var_x1 / (self.count - 1) if self.count > 0 else 0, dimension_values=[self.context.model_name])
        # self.input_mean_x2.add_or_update(value=self.mean_x2, dimension_values=[self.context.model_name])
        # self.input_var_x2.add_or_update(value=self.var_x2 / (self.count - 1) if self.count > 0 else 0, dimension_values=[self.context.model_name])
