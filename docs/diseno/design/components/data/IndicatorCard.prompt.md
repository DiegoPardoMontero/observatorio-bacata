Tarjeta de indicador para una localidad: muestra el valor en cifras tabulares, una tendencia descrita en palabras (sin verde/rojo), la fuente y la fecha de corte.

```jsx
<IndicatorCard kicker="Movilidad" locality="Kennedy" title="Tiempo medio de viaje al trabajo"
  value="58" unit="min" trend={{ direction: 'down', label: '4 min frente a 2025' }}
  compare="Bogotá: 62 min" source="Encuesta de Movilidad" cutoff="30 jun 2026" />
```

- `delayed` añade la marca "Datos con retraso"; acompáñala de un `DataDelayNotice` en la página.
- Siempre fuente y corte: una cifra sin fecha no se publica.
