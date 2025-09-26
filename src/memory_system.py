import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re
import math
from collections import Counter
import logging
from config import (
    MEMORY_FILE_PATH, SUMMARY_FILE_PATH, SHORT_TERM_MEMORY_LIMIT,
    LONG_TERM_SUMMARY_THRESHOLD, RELEVANCE_SEARCH_LIMIT, MAX_CONTEXT_TOKENS
)

logger = logging.getLogger(__name__)


class MemorySystem:
    def __init__(self):
        self.short_term_memory: List[Dict] = []
        self.conversation_summaries: List[Dict] = []
        self.ensure_data_directories()
        self.load_summaries()
    
    def ensure_data_directories(self):
        """Crear directorios de datos si no existen"""
        os.makedirs(os.path.dirname(MEMORY_FILE_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(SUMMARY_FILE_PATH), exist_ok=True)
    
    def add_interaction(self, user_message: str, assistant_response: str, metadata: Dict = None):
        """Agregar nueva interacción con metadata opcional"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "assistant_response": assistant_response,
            "metadata": metadata or {},
            "tokens_used": self._estimate_tokens(user_message + assistant_response),
            "relevance_score": 1.0  # Score inicial, se ajusta con el tiempo
        }
        
        # Agregar a memoria de corto plazo
        self.short_term_memory.append(interaction)
        
        # Mantener límite de memoria de corto plazo
        if len(self.short_term_memory) > SHORT_TERM_MEMORY_LIMIT:
            self.short_term_memory.pop(0)
        
        # Persistir en memoria de largo plazo
        self._save_to_long_term(interaction)
        
        # Verificar si necesita resumir
        self._check_and_summarize()
        
        logger.debug(f"Interacción agregada - Tokens: {interaction['tokens_used']}")
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimación aproximada de tokens (1 token ≈ 4 caracteres)"""
        return len(text) // 4
    
    def _save_to_long_term(self, interaction: Dict):
        """Guardar interacción en archivo persistente"""
        try:
            # Cargar historial existente
            history = []
            if os.path.exists(MEMORY_FILE_PATH):
                with open(MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Agregar nueva interacción
            history.append(interaction)
            
            # Guardar historial actualizado
            with open(MEMORY_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error guardando en memoria de largo plazo: {e}")
    
    def load_from_long_term(self):
        """Cargar historial desde archivo persistente"""
        try:
            if os.path.exists(MEMORY_FILE_PATH):
                with open(MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    
                # Cargar últimas interacciones a memoria de corto plazo
                recent_interactions = history[-SHORT_TERM_MEMORY_LIMIT:]
                self.short_term_memory = recent_interactions
                
                logger.info(f"Memoria cargada: {len(history)} total, {len(recent_interactions)} activas")
                print(f"Memoria cargada: {len(history)} conversaciones en total, {len(recent_interactions)} en memoria activa")
            else:
                logger.info("No se encontró historial previo")
                print("No se encontró historial previo. Iniciando nueva sesión.")
        except Exception as e:
            logger.error(f"Error cargando memoria de largo plazo: {e}")
    
    def search_relevant_conversations(self, query: str, limit: int = None) -> List[Dict]:
        """Búsqueda inteligente por relevancia usando TF-IDF simple"""
        if limit is None:
            limit = RELEVANCE_SEARCH_LIMIT
        
        try:
            # Cargar todo el historial
            all_history = []
            if os.path.exists(MEMORY_FILE_PATH):
                with open(MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                    all_history = json.load(f)
            
            if not all_history:
                return []
            
            # Calcular relevancia para cada conversación
            query_terms = self._extract_terms(query.lower())
            scored_conversations = []
            
            for conv in all_history:
                # Combinar mensaje del usuario y respuesta del asistente
                text = f"{conv['user_message']} {conv['assistant_response']}".lower()
                score = self._calculate_relevance_score(query_terms, text)
                
                if score > 0:
                    conv_copy = conv.copy()
                    conv_copy['relevance_score'] = score
                    scored_conversations.append(conv_copy)
            
            # Ordenar por relevancia y retornar los top N
            scored_conversations.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            logger.debug(f"Búsqueda relevante: {len(scored_conversations)} resultados para '{query}'")
            return scored_conversations[:limit]
            
        except Exception as e:
            logger.error(f"Error en búsqueda por relevancia: {e}")
            return []
    
    def _extract_terms(self, text: str) -> List[str]:
        """Extraer términos relevantes del texto"""
        # Limpiar y tokenizar
        text = re.sub(r'[^\w\s]', ' ', text)
        terms = text.split()
        
        # Filtrar palabras muy cortas y stop words básicas
        stop_words = {'el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'una', 'del', 'las', 'los', 'como', 'pero', 'sus', 'fue', 'ser', 'está', 'muy', 'más', 'todo', 'bien', 'puede', 'esto', 'sin', 'sobre', 'también', 'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todos', 'durante', 'ella', 'entre'}
        
        terms = [term for term in terms if len(term) > 2 and term not in stop_words]
        return terms
    
    def _calculate_relevance_score(self, query_terms: List[str], text: str) -> float:
        """Calcular score de relevancia usando frecuencia de términos"""
        text_terms = self._extract_terms(text)
        
        if not text_terms or not query_terms:
            return 0.0
        
        # Contar frecuencias
        text_freq = Counter(text_terms)
        
        score = 0.0
        for term in query_terms:
            if term in text_freq:
                # TF-IDF simplificado: frecuencia del término
                tf = text_freq[term] / len(text_terms)
                score += tf
        
        return score
    
    def _check_and_summarize(self):
        """Verificar si necesita resumir conversaciones antiguas"""
        try:
            if not os.path.exists(MEMORY_FILE_PATH):
                return
            
            with open(MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Si tenemos muchas conversaciones, resumir las más antiguas
            if len(history) >= LONG_TERM_SUMMARY_THRESHOLD:
                self._create_conversation_summary(history)
                
        except Exception as e:
            logger.error(f"Error verificando summarización: {e}")
    
    def _create_conversation_summary(self, history: List[Dict]):
        """Crear resumen de conversaciones antiguas"""
        try:
            # Tomar conversaciones que no están en memoria de corto plazo
            conversations_to_summarize = history[:-SHORT_TERM_MEMORY_LIMIT]
            
            if len(conversations_to_summarize) < 10:  # No resumir si hay pocas
                return
            
            # Crear resumen por períodos de tiempo
            summaries = self._group_conversations_by_time(conversations_to_summarize)
            
            # Guardar resúmenes
            self._save_summaries(summaries)
            
            logger.info(f"Creados {len(summaries)} resúmenes de conversación")
            
        except Exception as e:
            logger.error(f"Error creando resúmenes: {e}")
    
    def _group_conversations_by_time(self, conversations: List[Dict]) -> List[Dict]:
        """Agrupar conversaciones por períodos de tiempo para resumir"""
        summaries = []
        
        # Agrupar por semanas
        weekly_groups = {}
        
        for conv in conversations:
            try:
                date = datetime.fromisoformat(conv['timestamp'])
                week_key = f"{date.year}-W{date.isocalendar()[1]}"
                
                if week_key not in weekly_groups:
                    weekly_groups[week_key] = []
                
                weekly_groups[week_key].append(conv)
                
            except Exception:
                continue
        
        # Crear resúmenes por semana
        for week, convs in weekly_groups.items():
            if len(convs) >= 5:  # Solo resumir si hay suficientes conversaciones
                summary = self._create_weekly_summary(week, convs)
                summaries.append(summary)
        
        return summaries
    
    def _create_weekly_summary(self, week: str, conversations: List[Dict]) -> Dict:
        """Crear resumen de conversaciones de una semana"""
        # Analizar temas principales
        all_text = ' '.join([f"{c['user_message']} {c['assistant_response']}" 
                            for c in conversations])
        
        terms = self._extract_terms(all_text.lower())
        top_terms = Counter(terms).most_common(10)
        
        summary = {
            "period": week,
            "conversation_count": len(conversations),
            "date_range": {
                "start": conversations[0]['timestamp'],
                "end": conversations[-1]['timestamp']
            },
            "main_topics": [term for term, count in top_terms],
            "total_tokens": sum(c.get('tokens_used', 0) for c in conversations),
            "summary_text": f"Período {week}: {len(conversations)} conversaciones sobre temas como {', '.join([term for term, _ in top_terms[:5]])}"
        }
        
        return summary
    
    def _save_summaries(self, summaries: List[Dict]):
        """Guardar resúmenes de conversaciones"""
        try:
            existing_summaries = []
            if os.path.exists(SUMMARY_FILE_PATH):
                with open(SUMMARY_FILE_PATH, 'r', encoding='utf-8') as f:
                    existing_summaries = json.load(f)
            
            # Agregar nuevos resúmenes
            existing_summaries.extend(summaries)
            
            # Guardar
            with open(SUMMARY_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(existing_summaries, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error guardando resúmenes: {e}")
    
    def load_summaries(self):
        """Cargar resúmenes existentes"""
        try:
            if os.path.exists(SUMMARY_FILE_PATH):
                with open(SUMMARY_FILE_PATH, 'r', encoding='utf-8') as f:
                    self.conversation_summaries = json.load(f)
                    logger.debug(f"Cargados {len(self.conversation_summaries)} resúmenes")
        except Exception as e:
            logger.error(f"Error cargando resúmenes: {e}")
            self.conversation_summaries = []
    
    def get_intelligent_context(self, current_message: str, max_tokens: int = None) -> Tuple[List[Dict[str, str]], List[str]]:
        """Obtener contexto inteligente combinando memoria reciente y relevante"""
        if max_tokens is None:
            max_tokens = MAX_CONTEXT_TOKENS
        
        context_messages = []
        context_sources = []
        current_tokens = 0
        
        # 1. Siempre incluir memoria de corto plazo (más reciente)
        for interaction in reversed(self.short_term_memory):
            interaction_tokens = interaction.get('tokens_used', self._estimate_tokens(
                interaction['user_message'] + interaction['assistant_response']
            ))
            
            if current_tokens + interaction_tokens > max_tokens:
                break
            
            context_messages.insert(0, {"role": "user", "content": interaction["user_message"]})
            context_messages.insert(0, {"role": "assistant", "content": interaction["assistant_response"]})
            current_tokens += interaction_tokens
            context_sources.insert(0, "recent")
        
        # 2. Buscar conversaciones relevantes si queda espacio
        remaining_tokens = max_tokens - current_tokens
        if remaining_tokens > 200:  # Solo si queda espacio significativo
            relevant_conversations = self.search_relevant_conversations(
                current_message, limit=3
            )
            
            for conv in relevant_conversations:
                # No duplicar conversaciones que ya están en memoria reciente
                if not any(c for c in self.short_term_memory 
                          if c['timestamp'] == conv['timestamp']):
                    
                    conv_tokens = conv.get('tokens_used', self._estimate_tokens(
                        conv['user_message'] + conv['assistant_response']
                    ))
                    
                    if current_tokens + conv_tokens <= max_tokens:
                        context_messages.append({"role": "user", "content": conv["user_message"]})
                        context_messages.append({"role": "assistant", "content": conv["assistant_response"]})
                        current_tokens += conv_tokens
                        context_sources.append(f"relevant (score: {conv['relevance_score']:.2f})")
        
        # 3. Incluir resúmenes si están disponibles y hay espacio
        if self.conversation_summaries and remaining_tokens > 100:
            summary_text = self._get_relevant_summaries(current_message)
            if summary_text:
                summary_tokens = self._estimate_tokens(summary_text)
                if current_tokens + summary_tokens <= max_tokens:
                    context_messages.insert(0, {"role": "system", "content": f"Resumen de conversaciones anteriores: {summary_text}"})
                    context_sources.insert(0, "summary")
        
        logger.debug(f"Contexto generado: {current_tokens} tokens, fuentes: {context_sources}")
        return context_messages, context_sources
    
    def _get_relevant_summaries(self, query: str) -> str:
        """Obtener resúmenes relevantes para la consulta actual"""
        if not self.conversation_summaries:
            return ""
        
        query_terms = set(self._extract_terms(query.lower()))
        relevant_summaries = []
        
        for summary in self.conversation_summaries:
            summary_terms = set(summary.get('main_topics', []))
            if query_terms & summary_terms:  # Intersección de términos
                relevant_summaries.append(summary['summary_text'])
        
        return " ".join(relevant_summaries[:2])  # Máximo 2 resúmenes
    
    def clear_short_term(self):
        """Limpiar memoria de corto plazo"""
        self.short_term_memory = []
        logger.info("Memoria de corto plazo limpiada")
        print("Memoria de corto plazo limpiada.")
    
    def show_recent_history(self, limit: int = 5):
        """Mostrar historial reciente con información adicional"""
        if not self.short_term_memory:
            print("No hay historial reciente.")
            return
        
        print(f"\n--- Historial reciente (últimas {min(limit, len(self.short_term_memory))} interacciones) ---")
        recent = self.short_term_memory[-limit:]
        
        total_tokens = 0
        for i, interaction in enumerate(recent, 1):
            timestamp = interaction["timestamp"]
            user_msg = interaction["user_message"][:100] + "..." if len(interaction["user_message"]) > 100 else interaction["user_message"]
            assistant_msg = interaction["assistant_response"][:100] + "..." if len(interaction["assistant_response"]) > 100 else interaction["assistant_response"]
            tokens = interaction.get('tokens_used', 0)
            total_tokens += tokens
            
            print(f"{i}. [{timestamp}] ({tokens} tokens)")
            print(f"   Usuario: {user_msg}")
            print(f"   Asistente: {assistant_msg}")
            print()
        
        print(f"Total tokens en memoria reciente: {total_tokens}")
        print("--- Fin del historial ---\n")
    
    def get_memory_stats(self) -> Dict:
        """Obtener estadísticas de memoria"""
        try:
            total_conversations = 0
            total_tokens = 0
            
            if os.path.exists(MEMORY_FILE_PATH):
                with open(MEMORY_FILE_PATH, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    total_conversations = len(history)
                    total_tokens = sum(conv.get('tokens_used', 0) for conv in history)
            
            return {
                "total_conversations": total_conversations,
                "active_conversations": len(self.short_term_memory),
                "total_tokens": total_tokens,
                "summaries_count": len(self.conversation_summaries),
                "memory_file_size": os.path.getsize(MEMORY_FILE_PATH) if os.path.exists(MEMORY_FILE_PATH) else 0
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de memoria: {e}")
            return {}