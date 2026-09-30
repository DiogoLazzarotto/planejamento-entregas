# Planejamento de entregas

Aplicação local para cadastrar pedidos, criar viagens e atribuir cargas respeitando peso e data. API Python, banco SQLite e interface HTML/CSS/JavaScript. Projeto demonstrativo preparado com apoio de IA; produtores e veículos fictícios.

## Executar

Python 3.11+, sem dependências externas:

```bash
python server.py
```

Abra http://127.0.0.1:8000. O banco `planner.db` persiste entre execuções. Ctrl+C encerra. Porta alternativa: `python server.py --port 8001`.

## Demonstrar em dois minutos

1. Crie uma viagem no Caminhão A para 30/09/2026.
2. Planeje pedidos Alfa (6.000 kg) e Beta (8.000 kg): ocupação 14.000/16.000 kg.
3. Gama (10.000 kg) não cabe nessa viagem. Crie viagem com Caminhão B, mesma data, e atribua Gama.
4. Marque Alfa como entregue; a carga histórica permanece na viagem.
5. Desplaneje Beta ou cancele um pedido aberto; capacidade é liberada.
6. Reinicie o servidor: registros permanecem.

## API

| Método e rota | Corpo / resultado |
|---|---|
| GET `/api/state` | Veículos, viagens com carga e pedidos |
| POST `/api/orders` | `producer`, `product`, `day` ISO, `kg` inteiro positivo |
| POST `/api/trips` | `vehicle_id`, `day` ISO |
| POST `/api/assign` | `order_id`, `trip_id` |
| POST `/api/status` | `order_id`, `status`: entregue/cancelado/pendente |

## Regras e decisões

- Uma viagem por veículo/data; um pedido integral por viagem.
- Pedido pendente → planejado → entregue. Cancelamento: pendente ou planejado. Desplanejar: planejado → pendente.
- Datas devem coincidir; carga planejada + entregue não pode superar capacidade.
- `BEGIN IMMEDIATE` serializa atribuições antes de ler a carga, evitando concorrência que ultrapasse capacidade.
- SQL parametrizado; textos da interface renderizados com `textContent`.
- Banco não é servido como arquivo; servidor entrega apenas a pasta `web/`.

## Testar

```bash
python -m unittest discover -s tests -v
```

Testes verificam capacidade, rollback, datas, status, cancelamento, duplicidade e números inválidos.

## Limitações

Somente demonstração local (`127.0.0.1`), sem autenticação. Não expor como aplicação de produção. Não otimiza rotas, não permite fracionar pedidos, editar veículos, editar pedidos nem desfazer uma entrega concluída. SQLite dá persistência local; backup e controle multiusuário são evoluções futuras.

## Obter o projeto

```bash
git clone https://github.com/DiogoLazzarotto/planejamento-entregas.git
cd planejamento-entregas
```

[Voltar ao perfil](https://github.com/DiogoLazzarotto)
