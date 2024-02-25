# Relógios Temporais e Lógicos

## Tempo Físico

Tempo reportado pelos nossos relógios físicos

Poderiamos ficar tentados a utilizar este tempo físico para fazer decisões

* comparar eventos
* comparar versões de ficheiros
* decidir quem tem um relógio

Em geral nunca conseguimos sincronizar completamente os relógios.

**Não existe um tempo global**

Relatividade especial: tempo em referenciais diferentes parece passar de forma diferente

**Tempo físico não vale muito**

* não existe um tempo físico global
* atingi..


## Relógios lógicos

### Propriedades básicas

Tempo lógico é baseado em dados atualizados por programas

* contadores

Podem usar:

* uptades locais
* propagação em mensagens

Devem mimicar algumas propriedades do tempo físico: eventos do light cone passado devem ter tempos menores; eventos do light
cone futuro devem ter tempos maiores

### Condição lógica de Lamport

if a->b then C(a) < C(b) 

Se a acontece antes de b (happens-before) então o valor do relógio em a é menor que o 
valor do relógio em b 

### Relógios de Lamport

Cada valor de relógio é um inteiro, aumentando ao longo de cada caminho causal

Cada processo i tem um relógio L<sub>i</sub>

Um update (transicao de estado) ou envio incrementa o relógio

Um envio envia o relógio com a mensagem m como L<sub>m</sub>

Uma rececao de m guarda um mais o valor máximo de valores do relógio

L<sub>i</sub> := max(L<sub>i</sub>, L<sub>m</sub>) + 1


#### Vantagens e limitacoes

Vantagens:

* baratos de computar, guardar e enviar em mensagens
* pode ser utilizado para definir uma ordem total de eventos

Desvantagens:

* Relógios de Lamport apenas respeitam, não caracterizam o *happens-before*
    * comparar valores de relógio nao informa se os eventos são concorrentes
    * exceto quando os relógios acontecem de ter o mesmo valor

### Caracterizar o *happens-before*

Muitos relógios lógicos diferentes podem respeitar a condição do relógio

Para qualquer relógio lógico

a → b ⟹  C(a) < C(b)

faltam coisas 

### Historico causal

A historia causal de um evento é o oconjunto de eventos que aconteceram antes do mesmo mais o próprio evento

ℂ(e) = {e} 𝘜 { x | x → e }

Por definicao

e → e' ⇔ ℂ(e) ⊂ ℂ(e')

### Relógios vetoriais

Historias causais não devem ser utilizadas na prática

Podemos apenas guardar o número do último evento de cada processo

#### Operações com relógios vetoriais

Todos os eventos (update, send, receive) incrementam a componente própria (o processo i incrementa a posição i no mapa)

Vi\[i\] = Vi\[i\] + 1

Um send envia o relógio vetoriam com a mensagem m como Vm

Um receive também faz um max pointwise:

Vi := max(Vi, Vm)

Relógios comparados com funções de comparação padrão

Vi <= Vj ⟺  ∀p ⬝ Vi\[p\] <= Vj\[p\]

#### Número variável de nós

Um relógio vetorial utiliza um map que se adapta a um numero variavel de nos

Apenas temos que utillizar identificadores unicos para os nos

Cada id não mapeado é mapeado implicitamente para 0

Mas faz com que o relogio vetorial adquira mais entradas com o tempo

Retirar nós é complicado
