from ts.torch_handler.base_handler import BaseHandler
from ts.metrics.metric_type_enum import MetricTypes
from ts.utils.util import PredictionException
import torch
import json
from model import SimpleModel

class SimpleHandler(BaseHandler):
    def __init__(self):
        super(SimpleHandler, self).__init__()
        self.model = SimpleModel()
        self.count = 0
        self.mean_x1 = 0.0
        self.mean_x2 = 0.0
        self.var_x1 = 0.0
        self.var_x2 = 0.0

    
    def initialize(self, context):
        super().initialize(context)
        if context is None:
            print("Context is None!")
        else:
            print("Model Name:", context.model_name)        
        self.context = context
        metrics = context.metrics

        self.model.load_state_dict(torch.load("model.pth", map_location=torch.device('cpu')))
        self.model.eval()

        # metrics
        self.invalid_input_count = metrics.add_metric_to_cache(
            metric_name="invalid_input_count", 
            unit="count", 
            dimension_names=["Hostname"], 
            metric_type=MetricTypes.COUNTER
        )

        self.input_mean_x1 = metrics.add_metric_to_cache(
            metric_name="input_mean_x1", 
            unit="value", 
            dimension_names=["ModelName"], 
            metric_type=MetricTypes.GAUGE 
        )
        
        self.input_var_x1 = metrics.add_metric_to_cache(
            metric_name="input_var_x1", 
            unit="value", 
            dimension_names=["ModelName"], 
            metric_type=MetricTypes.GAUGE
        )

        self.input_mean_x2 = metrics.add_metric_to_cache(
            metric_name="input_mean_x2", 
            unit="value", 
            dimension_names=["ModelName"], 
            metric_type=MetricTypes.GAUGE 
        )
        
        self.input_var_x2 = metrics.add_metric_to_cache(
            metric_name="input_var_x2", 
            unit="value", 
            dimension_names=["ModelName"], 
            metric_type=MetricTypes.GAUGE
        )        


    def preprocess(self, data):

        #data processing
        preprocessed_data = data[0].get("data",None)
        if preprocessed_data is None:
            preprocessed_data = data[0]['body']['data']


        if len(preprocessed_data) != self.input_dim:
            self.invalid_input_count.add_or_update(value=1, dimension_values=[self.context.model_name])
            raise PredictionException(f"Invalid input dimensions. Expected {self.input_dim} but got {len(preprocessed_data)}.", 513) 
        preprocessed_data = torch.tensor(preprocessed_data).float()

        self.update_input_metrics(preprocessed_data)

        return preprocessed_data

    def inference(self, input_tensor):
        
        with torch.no_grad():
            output = self.model(input_tensor)
        
        #self.inf_request_count.add_or_update(value=1, dimension_values=[])

        # inference_count_metric = metrics.get_metric(
        #     metric_name="InferenceRequestCount", metric_type=MetricTypes.COUNTER
        # )
        # inference_count_metric.add_or_update(
        #     value=1, dimension_values=[self.context.model_name]
        # )        

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
        calculate incremental mean and variance
        """
        x1, x2 = preprocessed_data

        self.count += 1

        x1_delta = x1 - self.mean_x1
        x2_delta = x2 - self.mean_x2

        self.mean_x1 += x1_delta / (self.count)
        self.mean_x2 += x2_delta / (self.count)
        
        self.var_x1 += x1_delta * (x1 - self.mean_x1)
        self.var_x2 += x2_delta * (x2 - self.mean_x2)

        self.input_mean_x1.add_or_update(value=self.mean_x1, dimension_values=[self.context.model_name])
        self.input_var_x1.add_or_update(value=self.var_x1 / (self.count - 1) if self.count > 0 else 0, dimension_values=[self.context.model_name])
        self.input_mean_x2.add_or_update(value=self.mean_x2, dimension_values=[self.context.model_name])
        self.input_var_x2.add_or_update(value=self.var_x2 / (self.count - 1) if self.count > 0 else 0, dimension_values=[self.context.model_name])
