Leyenda para mapas por localidad: barra de clases con cortes tabulares, clave "Sin dato" rayada y contorno oro para la localidad elegida.

```jsx
<MapLegend title="Árboles por cada 1.000 habitantes" steps={5}
  ticks={['0','60','100','150','200','260']} selectedLabel="Kennedy" />
<MapLegend type="diverging" title="Frente al promedio de Bogotá" ticks={['−30 %','','','0','','','+30 %']} steps={5}
  lowLabel="Por debajo" highLabel="Por encima" />
```

- Secuencial para magnitudes; divergente sólo cuando hay un punto de referencia real (promedio, meta, cero).
