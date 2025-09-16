#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#  SPDX-License-Identifier: MIT-0

from aws_cdk import (
    aws_ssm as ssm,
)

import cfg


class PromptsStack:
    def __init__(self, cdk_scope):
        model_id_param = ssm.StringParameter(
            cdk_scope,
            "model_id",
            description="Parameter to store Llama4Scout Model ID",
            string_value="llama4scout",
        )

        summarization_prompt = ssm.StringParameter(
            cdk_scope,
            "summarization_prompt",
            simple_name=True,
            parameter_name=cfg.SSM_LLM_SUMMARIZATION_NAME,
            description="Prompt template for generating summary of overall chat",
            string_value="Please analyze the following transcript and provide a concise summary.\n\n"
            "Transcript: {transcript}\n\n"
            "Summary:",
        )

        topic_prompt = ssm.StringParameter(
            cdk_scope,
            "topic_prompt",
            parameter_name=cfg.SSM_LLM_TOPIC_PROMPT,
            description="Prompt template for finding primary topic",
            string_value="What is the main topic of this conversation? Examples: iPhone issue, billing problem, cancellation request.\n\n"
            "Transcript: {transcript}\n\n"
            "Topic:",
        )

        product_prompt = ssm.StringParameter(
            cdk_scope,
            "product_prompt",
            parameter_name=cfg.SSM_LLM_PRODUCT_PROMPT,
            description="Prompt template for finding products discussed",
            string_value="What product or service is this conversation about? Examples: internet service, mobile phone, broadband.\n\n"
            "Transcript: {transcript}\n\n"
            "Product:",
        )

        resolved_prompt = ssm.StringParameter(
            cdk_scope,
            "resolved_prompt",
            parameter_name=cfg.SSM_LLM_RESOLVED_PROMPT,
            description="Prompt template for generating resolutions",
            string_value="Did the agent successfully resolve the customer's issue? Answer with only 'yes' or 'no'.\n\n"
            "Transcript: {transcript}\n\n"
            "Resolution:",
        )

        callback_prompt = ssm.StringParameter(
            cdk_scope,
            "callback_prompt",
            parameter_name=cfg.SSM_LLM_CALLBACK_PROMPT,
            description="Prompt template for generating callback prompts",
            string_value="Was this a callback conversation? Answer with only 'yes' or 'no'.\n\n"
            "Transcript: {transcript}\n\n"
            "Callback:",
        )

        politeness_prompt = ssm.StringParameter(
            cdk_scope,
            "politeness_prompt",
            parameter_name=cfg.SSM_LLM_POLITE_PROMPT,
            description="Prompt template for checking politeness",
            string_value="Was the agent polite and professional throughout the conversation? Answer with only 'yes' or 'no'.\n\n"
            "Transcript: {transcript}\n\n"
            "Politeness:",
        )

        actions_prompt = ssm.StringParameter(
            cdk_scope,
            "actions_prompt",
            parameter_name=cfg.SSM_LLM_ACTION_PROMPT,
            description="Prompt template for generating actions",
            string_value="What specific actions did the agent take to help the customer?\n\n"
            "Transcript: {transcript}\n\n"
            "Actions:",
        )

        agent_feedback_prompt = ssm.StringParameter(
            cdk_scope,
            "agent_feedback_prompt",
            parameter_name=cfg.SSM_LLM_AGENT_SENTIMENT_PROMPT,
            description="Prompt template for agent sentiment analysis",
            string_value="Analyze the agent's sentiment in this conversation. Choose one: Positive, Negative, or Neutral.\n\n"
            "Transcript: {transcript}\n\n"
            "Agent Sentiment:",
        )

        customer_feedback_prompt = ssm.StringParameter(
            cdk_scope,
            "customer_feedback_prompt",
            parameter_name=cfg.SSM_LLM_CUSTOMER_SENTIMENT_PROMPT,
            description="Prompt template for customer sentiment analysis",
            string_value="Analyze the customer's sentiment in this conversation. Choose one: Positive, Negative, or Neutral.\n\n"
            "Transcript: {transcript}\n\n"
            "Customer Sentiment:",
        )

        self.model_id_param = model_id_param
        self.summarization_prompt = summarization_prompt
        self.topic_prompt = topic_prompt
        self.product_prompt = product_prompt
        self.resolved_prompt = resolved_prompt
        self.callback_prompt = callback_prompt
        self.politeness_prompt = politeness_prompt
        self.actions_prompt = actions_prompt
        self.agent_feedback_prompt = agent_feedback_prompt
        self.customer_feedback_prompt = customer_feedback_prompt
