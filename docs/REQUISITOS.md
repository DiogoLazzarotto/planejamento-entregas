# Requisitos e critérios de aceite

| ID | História | Critério de aceite | Evidência |
|---|---|---|---|
| RF01 | Como analista, quero consolidar produção por período | Somar ração em kg/t e categorias auxiliares em batidas, sem valores negativos | Testes do relatório e exemplo HTML |
| RF02 | Como analista, quero detectar entradas inválidas | Rejeitar categoria, data e números inválidos com linha do erro | Testes de validação |
| RF03 | Como gestor, quero consultar o volume logístico | Consultas reproduzíveis com carga fictícia e resultados documentados | demo.py e testes SQL |
| RF04 | Como operador, quero cadastrar pedidos | Nome, produto, data ISO e peso positivo obrigatórios | Testes do planejador |
| RF05 | Como operador, quero atribuir pedidos a veículos | Impedir carga acima da capacidade e data divergente | Testes transacionais |
| RF06 | Como operador, quero acompanhar a entrega | Permitir concluir pedido planejado e cancelar pedido aberto | Testes de transição |
| RF07 | Como visitante, quero avaliar projetos | Cards com escopo, tecnologia e links para código | Página de portfólio |

## Planejamento proposto

| Etapa | Entrega | Responsável | Situação |
|---|---|---|---|
| 1 | Relatórios e validações | Diogo | Implementada |
| 2 | Modelo e consultas SQL | Diogo | Implementada |
| 3 | Planejador e interface | Diogo | Implementada |
| 4 | Página e documentação | Diogo | Implementada |
| 5 | Estudo, revisão pessoal e demonstração | Diogo | Pendente |

Esse quadro documenta as entregas atuais; não simula sprints passadas, entrevistas ou validação com usuários.

## Backlog futuro

- RF08: importar arquivos XLSX com testes de células vazias e formatos numéricos.
- RF09: editar pedidos com recálculo transacional de capacidade.
- RF10: autenticar usuários antes de disponibilizar o planejador em rede.
- RF11: exportar programação semanal.

## Riscos

O planejador é uma demonstração local, sem autenticação. A atribuição é manual e não calcula distâncias nem rotas ótimas. Relatórios usam pesos informados; não inferem kg por batida. Testes automatizados verificam regras; validação com usuários permanece pendente.
