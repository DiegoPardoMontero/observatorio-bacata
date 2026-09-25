{# Pruebas genéricas propias, para no depender de paquetes externos. #}

{% test combinacion_unica(model, columnas) %}
select {{ columnas | join(', ') }}, count(*) as repeticiones
from {{ model }}
group by {{ columnas | join(', ') }}
having count(*) > 1
{% endtest %}

{% test en_rango(model, column_name, minimo=none, maximo=none) %}
select {{ column_name }}
from {{ model }}
where {{ column_name }} is not null
  and (
    false
    {% if minimo is not none %} or {{ column_name }} < {{ minimo }} {% endif %}
    {% if maximo is not none %} or {{ column_name }} > {{ maximo }} {% endif %}
  )
{% endtest %}
