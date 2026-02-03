"""
LLM service using Langchain + OpenAI GPT
"""
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Optional
import logging

from app.config.settings import settings
from app.core.exceptions import LLMException

logger = logging.getLogger(__name__)


# AI 상담사 시스템 프롬프트
CUSTOMER_SUPPORT_PROMPT = """당신은 친절하고 전문적인 AI 상담사입니다.

역할 및 목표:
- 고객의 문의사항을 정확히 이해하고 명확한 답변을 제공합니다
- 항상 예의 바르고 친절한 태도를 유지합니다
- 고객이 만족할 수 있도록 최선을 다해 도와드립니다

대화 가이드라인:
1. 고객의 말을 경청하고 공감하며 응답합니다
2. 간결하고 명확하게 답변합니다 (2-3 문장 이내)
3. 전문 용어는 피하고 쉬운 말로 설명합니다
4. 불확실한 정보는 추측하지 않고 솔직하게 말합니다
5. 필요시 추가 정보를 요청합니다

응답 형식:
- 전화 통화이므로 자연스럽고 구어체로 답변합니다
- 문장은 짧고 명확하게 유지합니다
- 불필요한 반복은 피합니다

제약사항:
- 개인정보나 민감한 정보는 요청하지 않습니다
- 법률, 의료, 재정 자문은 제공하지 않습니다
- 회사 정책 외의 약속은 하지 않습니다

당신의 목표는 고객이 만족스러운 상담 경험을 하도록 돕는 것입니다."""


class LLMService:
    """LLM service using Langchain + OpenAI GPT"""

    def __init__(self, persona: str = "customer_support"):
        """
        Initialize LLM service

        Args:
            persona: AI persona type ('customer_support', etc.)
        """
        try:
            self.llm = ChatOpenAI(
                model=settings.GPT_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                openai_organization=settings.OPENAI_ORG_ID,
                max_tokens=settings.GPT_MAX_TOKENS,
                temperature=settings.GPT_TEMPERATURE,
            )

            # Set system prompt based on persona
            self.system_prompt = self._get_system_prompt(persona)
            self.persona = persona

            logger.info(f"LLM service initialized with GPT model: {settings.GPT_MODEL}, persona: {persona}")

        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            raise LLMException(f"LLM initialization failed: {e}")

    def _get_system_prompt(self, persona: str) -> str:
        """
        Get system prompt based on persona

        Args:
            persona: AI persona type

        Returns:
            str: System prompt
        """
        prompts = {
            "customer_support": CUSTOMER_SUPPORT_PROMPT,
            # 추가 페르소나는 여기에 추가
        }

        return prompts.get(persona, CUSTOMER_SUPPORT_PROMPT)

    async def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate AI response to user message

        Args:
            user_message: User's message
            conversation_history: List of previous messages
                [{"role": "user"/"assistant", "content": "..."}]

        Returns:
            str: AI response text

        Raises:
            LLMException: If response generation fails
        """
        try:
            # Build message list
            messages = [SystemMessage(content=self.system_prompt)]

            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))

            # Add current user message
            messages.append(HumanMessage(content=user_message))

            logger.debug(f"Generating response for: '{user_message[:50]}...'")

            # Generate response
            response = self.llm.invoke(messages)

            # Extract text from response
            response_text = response.content.strip()

            logger.info(f"Generated response: '{response_text[:50]}...'")

            return response_text

        except Exception as e:
            logger.error(f"Failed to generate LLM response: {e}")
            raise LLMException(f"Response generation failed: {e}")

    async def generate_response_streaming(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ):
        """
        Generate AI response with streaming (for future optimization)

        Args:
            user_message: User's message
            conversation_history: List of previous messages

        Yields:
            str: Response chunks

        Raises:
            LLMException: If response generation fails
        """
        try:
            # Build message list
            messages = [SystemMessage(content=self.system_prompt)]

            if conversation_history:
                for msg in conversation_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))

            messages.append(HumanMessage(content=user_message))

            # Stream response
            async for chunk in self.llm.astream(messages):
                if hasattr(chunk, 'content'):
                    yield chunk.content

        except Exception as e:
            logger.error(f"Failed to stream LLM response: {e}")
            raise LLMException(f"Response streaming failed: {e}")


# Global LLM service instance
llm_service = LLMService(persona="customer_support")
