---
type: capture
status: archived
created: 2026-10-30
capture_id: 04db94e3-25f0-4ad7-b89f-fda291887e4f
---

# ZenyProjectHandler - decisões de leitura vetorial por poste e detector local

## Conteúdo capturado

Decisões de arquitetura tomadas em 2026-10-30 no ZenyProjectHandler. O sistema lê projetos de expansão da rede de distribuição da CEMIG a partir de PDFs. Ele tem um cliente Windows magro (PySide6) e um servidor em container (FastAPI, SQLite/Alembic, PyMuPDF, Tesseract).

Os documentos de origem são o design `docs/superpowers/specs/2026-10-30-leitura-vetorial-por-poste-design.md` e os ADRs 0016 e 0017, todos com estado "aceito". O ADR 0017 substitui parcialmente o ADR 0001: revoga a proibição de aprendizado de máquina.

### Problema (fato, segundo o design)

- A última rodada de curadoria avaliou 445 símbolos em 16 folhas: TP 140 / FP 66 / FN 305.
- Os erros que mais custam são símbolos não identificados e texto ou símbolo associado ao poste errado.
- Só o PDF chega, de quatro famílias vistas nos 16 PDFs de `examples/`:
  - Electric Office via "Microsoft: Print To PDF": 8 PDFs, texto da rede em contorno vetorial;
  - iText 5.5.13.3: 6 PDFs, texto nativo;
  - GPL Ghostscript: 1 PDF, contorno, sem texto;
  - AutoCAD 2023: 1 PDF, texto nativo, SHX e 11 camadas OCG.
- Todas as famílias têm ortofoto raster por baixo.

### Decisões

- **Decisão: não converter para DWG.** A conversão não traz informação nova, porque gera as mesmas linhas soltas que o PyMuPDF já lê, e exige SDK proprietário (ODA). DXF só existe como artefato de depuração.
- **Decisão: vetor primeiro, com modelo de desenho.**
  - Cada página vira um modelo de desenho derivado e descartável, guardado no cache do ADR 0004.
  - O modelo reúne texto recuperado, polilinhas e arcos reconstruídos, grupos candidatos a símbolo e camadas.
  - Um perfil por família de PDF escolhe a estratégia. A família é reconhecida por impressão estrutural, não só pelo campo `producer`.
  - Texto em contorno de glifo é lido por assinatura de forma normalizada, contra uma tabela de glifos versionada, em vez de OCR.
  - Glifo desconhecido vira diagnóstico, nunca palpite. O OCR fica como reserva até ser provado dispensável.
- **Decisão: sucesso medido por poste.**
  - Cada poste ganha uma ficha com identificador, estrutura, tipo de poste, coordenada UTM, vãos (comprimento e cabo) e símbolos associados.
  - Uma conferência ajusta a transformação página → UTM e marca como pendência a posição ou o vão que divergirem.
  - Tolerâncias iniciais (calibráveis na F4): vão até `max(2 m, 3%)`, posição até 3 m.
  - Antiobjetivo: uma ficha errada apresentada com segurança.
- **Decisão: substituição só com prova.**
  - O analisador novo tem versão própria e roda em paralelo ao atual.
  - Ele só vira padrão quando for ≥ o atual em todas as métricas por poste, sem regressão por folha.
  - Só então saem os detectores substituídos e, se nenhuma família precisar, o OCR e o Tesseract.
- **Decisão: detector visual local, só para o resíduo.**
  - Roda com ONNX Runtime em CPU no servidor, como evidência com confiança. O hash dos pesos entra na assinatura do analisador.
  - Licença do modelo e do código de treino: Apache-2.0, BSD ou MIT. YOLO Ultralytics (AGPL) está excluído.
  - O treino roda na máquina do usuário (Windows, GPU AMD RX 9070 XT, PyTorch com ROCm nativo ou via WSL2). O suporte a essa GPU será validado por um spike no início da F7; se falhar, treino em CPU ou GPU alugada, que ainda depende de aval do usuário.
  - Dados, rótulos e pesos ficam fora do Git. Os pesos são artefato de release com SHA-256.
- **Decisão: Claude só para rotular dados de treino.**
  - O fluxo de rotulagem tem pré-marcação vetorial, leitura dupla cega por subagentes e amostra humana de cerca de 5 folhas em 50 por lote.
  - O usuário autorizou o envio das folhas à Anthropic para esse fim (LGPD e contrato).
  - Os rótulos podem alimentar o treino, o que revisa um invariante do contrato de curadoria.
  - A avaliação usa folhas novas, reservadas antes de qualquer correção, lidas às cegas, congeladas e nunca usadas no treino. As 16 folhas atuais servem só de desenvolvimento.
  - Claude em produção foi descartado: custo por folha, resultado não determinístico e serviço externo.
- **Decisão: F0 é limpeza.**
  - Sai o que é de etapa encerrada: scripts `benchmark_*_e0N`, `*_e13`, `*_e14`, `*_e16*`, `stage1N_*`, `visual_qa_*` e `scripts/experiments/`, o roadmap de curadoria paralela (a E11 fica sem efeito) e o histórico narrativo do README.
  - Pronto quando o gate completo fica verde, sem mudança de comportamento.

### Fases (resumo do agente)

| Fase | Entrega |
|---|---|
| F0 | limpeza |
| F1 | medição por poste e baseline |
| F2 | modelo de desenho e tabela de glifos |
| F3 | símbolos e ficha do poste |
| F4 | conferência UTM |
| F5 | troca do analisador |
| F6 | fluxo contínuo de rótulos, cerca de 50 folhas por mês; pode começar a partir da F2 |
| F7 | detector local; depende de volume da F6 |

### Alternativas descartadas (segundo o design)

- Conversão para DWG.
- Claude no servidor a cada análise.
- OCR em DPI maior.
- Treinar um detector antes de medir o vetor.

### Opinião do usuário

O usuário pede documentação enxuta. O design limita os documentos a ele mesmo, aos ADRs 0016 e 0017 e a atualizações pontuais em `CLAUDE.md` e no contrato de curadoria, sem histórico de execução em arquivo versionado.

## Contexto

Sessão de arquitetura no repositório do ZenyProjectHandler. O escriba recebeu o pedido de registrar as decisões e conferiu o resumo contra os três documentos, lidos diretamente no repositório.

## Origem

- Projeto: ZenyProjectHandler, `C:\Users\Caio\Desktop\repos\ZenyProjectHandler`
- Base: commit `1523aa1c24f30f1ed9166c2e950d78859a8f87a8`. Os documentos ainda não têm commit: o design e os ADRs 0016/0017 são arquivos novos, e o ADR 0001 e o `CLAUDE.md` estão modificados.
- Arquivos:
  - `docs/superpowers/specs/2026-10-30-leitura-vetorial-por-poste-design.md`
  - `docs/adr/0016-leitura-vetorial-com-modelo-de-desenho.md`
  - `docs/adr/0017-detector-visual-local-e-rotulagem-assistida.md`
  - `docs/adr/0001-arquitetura-modular-sem-analisador-obrigatorio.md` (parcialmente substituído)

## Por que registrar

- Guarda o raciocínio de uma virada de rumo: de OCR sobre raster para leitura vetorial, com o sucesso medido por poste.
- Registra os limites aceitos para IA: detector local com licença permissiva e Claude só como rotulador, com avaliação cega separada.
- O padrão pode servir a outros projetos que leem PDFs técnicos: analisar o vetor como desenho, ler glifos por assinatura de forma e medir pela unidade que importa ao usuário.

## Limitações e incertezas

- Os documentos estão sem commit e podem mudar antes de entrar no Git. O hash exato que os versionará é desconhecido.
- Os arquivos não foram copiados. Só existem no caminho local do repositório acima.
- Hipóteses ainda não confirmadas (o design as deixa para a F2): cada forma pequena preenchida é um glifo; os símbolos da rede são vetoriais em todas as famílias; as imagens das folhas Print To PDF são só ladrilhos da ortofoto.
- Não verificado:
  - o suporte do ROCm à RX 9070 XT, pendente de spike;
  - as tolerâncias UTM e o orçamento de 60 s de inferência por folha em CPU, valores iniciais "por conta" do arquiteto;
  - a arquitetura do detector, deixada a quem constrói (exemplos citados: RT-DETR, Faster R-CNN do torchvision).
- A autorização de envio à Anthropic consta nos documentos como dada pelo usuário. O escriba não a conferiu diretamente.

## Possíveis conexões

- Não há nota do projeto ZenyProjectHandler no vault. Ele é distinto do projeto ZenyHotelManager.
- Temas: leitura vetorial de PDF técnico, rotulagem assistida por LLM com auditoria humana, avaliação cega separada do treino, licenças de modelos de visão (AGPL vs Apache/MIT).
