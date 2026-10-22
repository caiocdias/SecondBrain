---
type: knowledge
status: processed
created: 2026-10-22
projects:
  - "[[ZenyHotelManager]]"
sources:
  - "[[2026-10-22 - ZenyHotelManager - Tipos do kernel - 8406864a]]"
---
# ZenyHotelManager - Tipos do kernel

Referência técnica do projeto [[ZenyHotelManager]]: Money, Percent, IDs, números legíveis, CPF/CNPJ, cifragem, tokens selados, índice cego, ator corrente e Clock.

Texto literal do `CLAUDE.md` do repositório, linhas 107–119, no commit `a6c0f03` (2026-10-22), escrito pelos agentes que executaram as etapas M0 E01 a M5 E03; integrado sem resumo nem reescrita. Referências como "SPEC", "ARCHITECTURE §x", "RF-…", "RN-…", "Hn" e "Mx Ey" apontam para `docs/SPEC.md`, `docs/ARCHITECTURE.md` e `docs/roadmaps/` do repositório; menções a uma seção (por exemplo, seção "Transições de hospedagem") apontam para outra parte do antigo `CLAUDE.md`, hoje numa das notas de tema listadas no hub. Mudanças posteriores chegam por capturas "ZenyHotelManager - atualização Mx Ey" (fluxo no hub).

---

**Tipos do kernel** (RN-02, D15, D16, ARCHITECTURE §7, §8.3 e §11): a API pública fica na raiz de `com.zeny.hotel.shared`; nenhum módulo cria tipo próprio para estes conceitos.

- **Dinheiro:** sempre `Money` (BRL, `BigDecimal` com 2 casas); nunca `Double`/`Float` nem `BigDecimal` solto. `Money.of("12.50")` é exato e recusa mais de 2 casas. Arredondar só com `Money.round(...)`, a regra única (`Money.ROUNDING_MODE`, hoje `HALF_EVEN`); `money * fator` e `money * percent` já passam por ela. Para repartir um valor, use `allocate(pesos)` ou `split(n)` (método do maior resto: as partes somam exatamente o total). Coluna `numeric(14,2)`; em JSON, string `"123.45"`. O `MoneyConverter` é aplicado automaticamente.
- **Percentual:** `Percent` em pontos percentuais com 4 casas (`12.5` = 12,5%), coluna `numeric(7,4)`, string em JSON; `percent.of(money)` arredonda pela regra de `Money`.
- **IDs:** cada agregado declara `@JvmInline value class XId(override val value: UUID) : TypedId` e gera com `UuidV7.generate()`; coluna `uuid`. Na entidade o id fica desembrulhado e o Hibernate o mapeia direto, então busque com `em.find(X::class.java, id.value)` e declare `JpaRepository<X, UUID>`. Numa coleção (`Set<XId>`), use `@Convert` com uma subclasse de `TypedIdConverter`; sem ela, o contexto não sobe.
- **Números legíveis:** `DocumentNumberGenerator.next(DocumentNumberType("R", "<módulo>.<sequence>"), ano)` devolve `R-2026-000123`. O módulo cria a sequence na sua migração, e o ano vem da data operacional. A sequência não reinicia por ano e pode ter buracos (rollback), então não serve para numeração fiscal. Coluna `varchar`, com conversor automático.
- **Documentos e endereço:** `Cpf` e `Cnpj` (inclusive o alfanumérico) validam o dígito verificador e guardam só dígitos/caracteres (`varchar(11)`/`varchar(14)`, conversores automáticos). `Address` é `@Embeddable`: endereço no Brasil com o código IBGE do município (7 dígitos, coerente com a UF).
- **Conteúdo sensível (bytes):** `ContentCipher` (`FieldEncryption.kt`, implementação `AesGcmContentCipher`) cifra `ByteArray` com AES-256-GCM sobre o mesmo `EncryptionKeyRing` do `FieldCipher` (mesmas chaves e id da chave no resultado, `ZNC1` ‖ id ‖ nonce ‖ cifra ‖ tag), com um dado associado de quem chama (o `files` usa o id do anexo: o conteúdo de um não decifra como outro). Em memória: para anexos com limite de tamanho. Falha com `FieldDecryptionException`.
- **Tokens selados:** `TokenSealer` (`FieldEncryption.kt`, implementação `HkdfTokenSealer`) sela um texto para uma finalidade com AES-256-GCM e uma chave **derivada** por HKDF-SHA256 de cada chave do anel (`info` = finalidade), formato `t1:<id da chave>:<base64url>`. Nunca use o `FieldCipher` para tokens que o servidor emite e depois aceita: ele cifra colunas com texto que o usuário escolhe, e um valor de coluna viraria token. A rotação segue a do anel (o id da chave vai no token).
- **Coluna cifrada pesquisável (índice cego, H8 do M3):** `BlindIndex` (`FieldEncryption.kt`, implementação `HmacBlindIndex` em `shared/infrastructure/crypto/`) calcula o HMAC-SHA256 de um valor **já normalizado** com uma chave **derivada** por HKDF-SHA256 de cada chave do anel (`info` = finalidade; sal e prefixo próprios, nunca a chave das colunas nem a dos tokens). Grave `compute(finalidade, valor)` (o id da chave e o hash, base64url de 43 caracteres) em duas colunas ao lado da coluna cifrada, com índice no hash, e busque por `hash IN (:candidates)` com `candidates(finalidade, valor)` (um hash por chave do anel, a ativa primeiro): o que foi indexado antes de uma rotação continua encontrável enquanto a chave antiga seguir no anel; antes de retirá-la, reindexe as linhas cujo id de chave não é o ativo (`BlindIndex.activeKeyId`), como faz o `GuestDocumentRekeyJob` do `guests` (procedimento em "Chaves de cifragem"). Normalize antes (dígitos, maiúsculas, tipo e país) e nunca leia a coluna cifrada na busca. O primeiro uso é o número de documento do `guests` (`IdDocuments.INDEX_PURPOSE`); `fnrh` e `reservations` buscam pela `GuestsApi.findByDocument`, nunca pelo próprio índice. Valor curto e de domínio pequeno (raça/cor) não vai cifrado sozinho: o AES-GCM preserva o tamanho, então junte e complete até um tamanho fixo antes de cifrar (`SensitiveGuestData.encode`).
- **Dados sensíveis** (credenciais de integração, sensíveis da FNRH, número de documento): `@Convert(converter = EncryptedStringConverter::class)` num atributo `String` com coluna `text`, ou `FieldCipher` injetado. O valor gravado é `v1:<id da chave>:<base64url>`, com nonce aleatório por valor, e por isso a coluna cifrada não serve para busca nem índice. CPF cifrado: grave `cpf.digits` numa coluna cifrada.
- **Ator corrente** (`Actors.kt`, ARCHITECTURE §8.1): `UserId` e `DeviceSessionId` são ids do kernel (todo módulo referencia usuários sem depender de `iam`); injete `CurrentActor` e chame `current()` (sem token, `401 UNAUTHENTICATED`) ou `currentOrNull()`. A implementação (`iam`) lê o access token validado (`sub` e `sid`). Só `staff` e `notifications` importam `iam`, e só a API pública `IamApi` (H9 do M2; o `ModularityTest` barra outro módulo). Também do kernel e implementados pelo `iam` (M2 E04, H8): a porta `DeviceSessionStatus` (`isRevoked(sessionId)`: o access token de uma sessão revogada ainda vale até vencer) e o evento `DeviceSessionsRevoked(userId, sessionIds)` (UUIDs), publicado na transação de toda revogação de sessão.
- **Tempo:** injete `java.time.Clock` (bean UTC em `shared/infrastructure/time/`) em vez de chamar `Instant.now()`; um teste fixa o tempo declarando o seu próprio bean `Clock`. Horário do dia (`LocalTime`) fica em coluna `time` e data de negócio (`LocalDate`) em `date`: o Hibernate os entrega ao driver como `java.time` (`hibernate.type.java_time_use_direct_jdbc`, M1 E06), sem deslocar pelo fuso da JVM.

---

## Proveniência

- 2026-10-22 — [[2026-10-22 - ZenyHotelManager - Tipos do kernel - 8406864a]] (capture_id: 8406864a-13fc-4012-b915-4be15129ba49): texto literal do `CLAUDE.md` do repositório ZenyHotelManager (linhas 107–119, commit `a6c0f03`), integrado sem alteração; o tipo Knowledge em `20 Knowledge/` foi escolhido pelo usuário no processamento.
