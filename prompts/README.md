# 📝 Diretório de Prompts

Este diretório contém todos os templates de prompts usados pelo sistema.

## 📋 Estrutura de Nomenclatura

### System Prompts (Persona + Output Format)
- `system_conceptual_explanation.txt` - Explicação conceitual com Chain-of-Thought
- `system_practical_examples.txt` - Exemplos práticos e analogias
- `system_reflection_questions.txt` - Questões reflexivas (Taxonomia de Bloom)
- `system_visual_summary.txt` - Mapas mentais e resumos visuais

### User Prompts (Instruções + Contexto)
- `user_conceptual_explanation.txt` - Instruções para explicação conceitual
- `user_practical_examples.txt` - Instruções para exemplos práticos
- `user_reflection_questions.txt` - Instruções para questões reflexivas
- `user_visual_summary.txt` - Instruções para resumo visual

### Templates
- `template_student_context.txt` - Template do contexto do estudante

## 🔧 Variáveis Disponíveis

Todos os prompts podem usar as seguintes variáveis (substituídas pelo motor):

### Do Perfil do Estudante:
- `{nome}` - Nome do estudante
- `{idade}` - Idade em anos
- `{nivel}` - Nível (Iniciante/Intermediário/Avançado)
- `{estilo_aprendizagem}` - Estilo de aprendizagem
- `{interesses}` - Lista de interesses (como string)
- `{descricao}` - Descrição adicional

### Contextos Gerados:
- `{student_context}` - Contexto completo formatado do estudante
- `{topic}` - Tópico educacional
- `{interests_hint}` - Dica sobre interesses (opcional)

## ✏️ Como Editar Prompts

1. **Identifique o prompt**: Determine qual tipo de conteúdo você quer melhorar
2. **Edite o arquivo correspondente**: Mantenha as variáveis `{variavel}` intactas
3. **Teste**: Gere conteúdo e valide a qualidade
4. **Versione**: Considere criar backups antes de mudanças grandes

## 🎯 Boas Práticas

- ✅ Mantenha as variáveis entre chaves `{}`
- ✅ Preserve a estrutura JSON no system prompt
- ✅ Use linguagem clara e diretiva
- ✅ Teste mudanças com diferentes perfis de estudantes
- ✅ Documente mudanças significativas

## 🔄 Versionamento

Para criar versões alternativas de prompts:
- Adicione sufixo: `system_conceptual_explanation_v2.txt`
- Configure no código qual versão usar
- Mantenha prompts antigos para comparação A/B

## 📊 Técnicas de Prompt Engineering Implementadas

1. **Persona Prompting**: Definido no início de cada system prompt
2. **Output Formatting**: Estrutura JSON obrigatória
3. **Chain-of-Thought**: Explícito em conceptual_explanation
4. **Context Setting**: Via template_student_context.txt
5. **Taxonomia de Bloom**: Estruturada em reflection_questions
