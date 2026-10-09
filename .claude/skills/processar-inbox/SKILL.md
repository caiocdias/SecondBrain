---
name: processar-inbox
description: Processa e incorpora as capturas pendentes de 00 Inbox/ deste Second Brain como agente curador. Use quando o usuário pedir para processar, incorporar ou integrar a Inbox, ou retomar um processamento interrompido. Só opera em sessão iniciada na raiz do vault.
argument-hint: "[capturas específicas (opcional)]"
---

# Processar Inbox (curador)

Escopo opcional informado pelo usuário: $ARGUMENTS
Se vazio, processe todas as capturas pendentes.

`99 System/AI/processing.md` é o protocolo oficial. Esta skill resume a ordem de execução; em caso de divergência, siga o protocolo.

## 1. Verificar o papel

- Confirme que a sessão foi iniciada na raiz do vault (AGENTS.md e `99 System/AI/` no diretório principal). Caso contrário, pare e explique que o processamento exige uma sessão dedicada ao vault.
- Leia AGENTS.md, `schemas.md`, `ingestion.md`, `processing.md` e `mutation-policy.md`.

## 2. Preparar o lote

- Procure em `50 Logs/` um lote anterior sem conclusão e confira seus artefatos pelo capture_id; retome a partir deles sem duplicar integrações.
- Enumere as pendentes: arquivos `.md` em `00 Inbox/` com `type: capture` e `status: inbox`. Ignore `.gitkeep`, temporários e templates; anexos isolados não são notas.
- Capturas manuais sem capture_id recebem um identificador antes do processamento.
- Registre o início do lote em `50 Logs/`.

## 3. Processar cada captura, uma por vez

1. Ler a captura e conferir as referências necessárias.
2. Buscar notas equivalentes (títulos, aliases, properties, conteúdo).
3. Escolher a menor integração útil: enriquecer nota existente, criar Source, Knowledge ou metodologia em `draft`, vincular a projeto real, arquivar como histórico/duplicata, ou manter na Inbox registrando a pendência.
4. Executar, incluindo proveniência e capture_id nas notas que recebem a integração.
5. Validar links.
6. Mover a captura para `90 Archive/Inbox/` com `status: archived`; anexos permanentes vão para `30 Sources/Attachments/`, com links conferidos.
7. Atualizar o log do lote.

## 4. Limites

- Mudanças amplas (exclusão definitiva, renomeação ou fusão em massa, schema global, reorganização estrutural, promoção a `canonical`) → prepare uma proposta e não execute.
- Mudanças locais cobertas pelo processamento seguem sem confirmações repetitivas.
- Se outra sessão estiver processando ou uma captura mudar durante a leitura, preserve o estado e relate.
- Nunca invente fontes ou evidências.

## 5. Concluir

- Marque o lote como concluído no log após as verificações.
- Mostre `git status` e ofereça um commit local; não faça push.
- Resuma: capturas processadas, notas criadas ou enriquecidas, capturas mantidas na Inbox e pendências.
