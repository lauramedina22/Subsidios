# Documento Técnico del Proyecto

---

## 1. Nombre del Proyecto

**Sistema de Gestión de Subsidio de Alimentación — Bienestar Universitario**

---

## 2. Integrantes

| Nombre | Rol |
|--------|-----|
| [Nombre del integrante 1] | [Rol] |
| [Nombre del integrante 2] | [Rol] |
| [Nombre del integrante 3] | [Rol] |

---

## 3. Objeto de Negocio

La Universidad de Caldas, a través de su área de Bienestar Universitario, administra un programa de subsidio de alimentación dirigido a estudiantes de estratos 1, 2 y 3. El programa busca garantizar el acceso a una alimentación balanceada y de calidad durante el horario académico, promoviendo la permanencia estudiantil y el bienestar integral.

El sistema gestiona los siguientes procesos:

- **Proveedores**: Empresas contratadas para suministrar los alimentos en cada sede.
- **Sedes**: Puntos físicos de distribución (comedores universitarios) con capacidad y horarios definidos.
- **Estudiantes**: Beneficiarios del subsidio, con seguimiento por semestre, estrato y tipo de alimentación.
- **Menús Diarios**: Planificación de platos (carnívoros y vegetarianos) con información nutricional, ingredientes y alertas de alérgenos.
- **Consumos**: Registro diario de asistencia de cada estudiante al comedor, con validación de identidad.
- **Evaluaciones**: Calificación y retroalimentación de los estudiantes sobre la calidad del servicio y los alimentos.

---

## 4. Objetivo General

Desarrollar una aplicación web para la gestión integral del subsidio de alimentación universitaria, permitiendo administrar proveedores, sedes, estudiantes, menús, consumos y evaluaciones mediante una interfaz moderna e intuitiva con almacenamiento en base de datos NoSQL (MongoDB).

---

## 5. Objetivos Específicos

1. Diseñar un modelo de datos NoSQL híbrido que combine documentos embebidos para consultas frecuentes (consumos, menús, evaluaciones) con referencias para relaciones entre colecciones independientes (proveedores → sedes).
2. Implementar operaciones CRUD completas para las seis colecciones del sistema (proveedores, sedes, estudiantes, menús, consumos, evaluaciones).
3. Desarrollar una interfaz de usuario con Streamlit que permita la visualización, creación, edición y eliminación de registros con paginación y filtros.
4. Implementar consultas de agregación que proporcionen indicadores clave como total de consumos, promedio de calificaciones y capacidad ocupada.
5. Generar datos de prueba masivos (50,000+ estudiantes, 100,000+ consumos, 15,000+ menús) para validar el rendimiento del sistema.

---

## 6. Esquema de Solución

La solución se desarrolló utilizando **MongoDB**, una base de datos NoSQL orientada al almacenamiento de documentos en formato JSON. La base de datos, llamada `comedor_universitario`, está compuesta por **seis colecciones principales**: `proveedores`, `sedes`, `estudiantes`, `menus`, `consumos` y `evaluaciones`.

Para poblar la base de datos se crearon scripts en Python utilizando la librería PyMongo, los cuales generan automáticamente datos de prueba de manera reproducible. Gracias a este proceso, se obtuvo un conjunto de aproximadamente **979 mil registros** (367,200 consumos + 411,833 estudiantes + 200,065 evaluaciones), lo que permite simular un entorno con un volumen de información similar al de un sistema real.

La interacción con la base de datos se realiza mediante una aplicación web desarrollada en **Streamlit**, que se conecta a **MongoDB Atlas** a través de PyMongo para ejecutar consultas, registrar información y visualizar los datos almacenados.

La distribución de los datos no es homogénea. La mayor cantidad de registros se concentra en las colecciones de `estudiantes` (411,833 documentos) y `consumos` (367,200 documentos), mientras que colecciones como `proveedores` y `sedes` contienen pocos registros debido a su naturaleza administrativa. Por esta razón, el diseño de la base de datos fue optimizado mediante el uso de índices y técnicas de desnormalización, permitiendo realizar consultas rápidas incluso cuando se trabaja con grandes volúmenes de información.

En cuanto al modelo de datos, cada documento conserva su identificador único generado por MongoDB (`_id`). Las relaciones entre colecciones se manejan principalmente mediante referencias a estos identificadores. Sin embargo, para mejorar el rendimiento en las consultas más frecuentes, algunos documentos incluyen información adicional incrustada, como el nombre del estudiante, su código y el tipo de almuerzo asociado. De esta forma se reduce la necesidad de realizar búsquedas adicionales entre colecciones y se mejora la eficiencia del sistema.

### Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Frontend | Streamlit 1.35+ |
| Backend | Python 3.12+ |
| Base de datos | MongoDB Atlas (cloud) |
| Driver MongoDB | PyMongo |
| Conexión | URI con autenticación |
| Estilos | CSS personalizado + Font Awesome |
| Control de versiones | Git |

### Conexión a Base de Datos

La conexión se realiza a través de una instancia de MongoDB Atlas usando variables de entorno:

- URI: `mongodb+srv://<usuario>:<password>@cluster0.bjvwjq5.mongodb.net/`
- Base de datos: `comedor_universitario`
- Tiempo de espera de conexión: 5 segundos

---

## 7. Justificación del Modelo

Se optó por MongoDB como motor de base de datos por su **flexibilidad de esquema**, que permite que colecciones como `menus` evolucionen agregando campos como `info_nutricional` sin migraciones complejas; su capacidad de **documentos embebidos**, que evita joins costosos al representar relaciones frecuentes (ej: `consumo.estudiante_id` embebe `nombre_completo`, `codigo_estudiante` y `tipo_almuerzo`); su **escalabilidad horizontal** en MongoDB Atlas para volúmenes grandes (50,000+ estudiantes); y sus **agregaciones nativas** mediante pipeline para calcular estadísticas directamente en la base de datos.

La estrategia de modelado es **híbrida**: cada documento tiene un `_id` autogenerado (ObjectId). Las relaciones con alta densidad de consultas se resuelven con **documentos embebidos** — consumos, menús y evaluaciones incrustan un extracto desnormalizado de los campos más consultados de sus colecciones referenciadas. Las relaciones entre colecciones independientes, como `sede.proveedor_id` → `proveedores`, se resuelven mediante **referencias por ObjectId**. Adicionalmente, cada colección cuenta con **validación a nivel de esquema** mediante `$jsonSchema` de MongoDB, garantizando la integridad de tipos y campos requeridos en todos los documentos.

---

## 8. Esquema Jerárquico

```
Subsidio de Alimentación
│
├── Proveedores
│   ├── _id: ObjectId
│   ├── nombre_empresa
│   ├── nit
│   ├── contacto_nombre
│   ├── telefono
│   ├── correo
│   ├── frecuencia_entrega
│   └── estado_activo
│
├── Sedes
│   ├── _id: ObjectId
│   ├── nombre_sede
│   ├── ubicacion
│   ├── capacidad_maxima
│   ├── horario_atencion { apertura, cierre }
│   ├── estado_activo
│   └── proveedor_id: ObjectId ═════> Proveedores (referencia)
│
├── Estudiantes
│   ├── _id: ObjectId
│   ├── codigo_estudiante
│   ├── nombre_completo
│   ├── correo
│   ├── telefono
│   ├── facultad
│   ├── programa
│   ├── semestre
│   ├── estrato
│   ├── fecha_inicio_subsidio
│   ├── fecha_fin_subsidio
│   ├── tipo_almuerzo
│   └── subsidio_activo
│
├── Menús
│   ├── _id: ObjectId
│   ├── sede_id { nombre_sede, ubicacion } (embebido) ══> Sedes
│   ├── fecha
│   ├── tipo_comida (carnivoro | vegetariano)
│   ├── plato
│   ├── info_nutricional { calorias, proteinas, carbohidratos, grasas }
│   ├── ingredientes [ ]
│   └── advertencia_alergias [ ]
│
├── Consumos
│   ├── _id: ObjectId
│   ├── estudiante_id { nombre_completo, codigo_estudiante, tipo_almuerzo } (embebido) ══> Estudiantes
│   ├── sede_id { nombre_sede, ubicacion } (embebido) ══> Sedes
│   ├── menu_id { plato, tipo_comida } (embebido) ══> Menús
│   ├── fecha_consumo
│   ├── hora_ingreso
│   └── validacion_identidad
│
└── Evaluaciones
    ├── _id: ObjectId
    ├── estudiante_id { nombre_completo, codigo_estudiante, semestre, fecha_inicio_subsidio, fecha_fin_subsidio } (embebido) ══> Estudiantes
    ├── sede_id { nombre_sede, ubicacion } (embebido) ══> Sedes
    ├── menu_id { plato, tipo_comida } (embebido) ══> Menús
    ├── fecha_evaluacion
    ├── calificacion (1-5)
    ├── comentario
    └── sugerencias
```

---

## 9. Descripción de Colecciones y Documentos

### 9.1 Proveedores

Información de las empresas contratadas para suministrar los alimentos: datos de contacto, identificación tributaria y estado operativo. Es la colección raíz de la que dependen las sedes.

```json
{
  "_id": ObjectId("..."),
  "nombre_empresa": "Distribuidora ABC",
  "nit": "900123456-7",
  "contacto_nombre": "Carlos Pérez",
  "telefono": "3001234567",
  "correo": "contacto@abc.com",
  "frecuencia_entrega": "Semanal",
  "estado_activo": true
}
```

### 9.2 Sedes

Puntos físicos de distribución (comedores universitarios) con ubicación geográfica, capacidad máxima, horario de atención y estado operativo. Cada sede se asocia a un proveedor mediante referencia por ObjectId.

```json
{
  "_id": ObjectId("..."),
  "nombre_sede": "Sede Central",
  "ubicacion": "Calle 65 N 26-10, Manizales, Caldas",
  "capacidad_maxima": 300,
  "horario_atencion": {
    "apertura": "11:00",
    "cierre": "15:00"
  },
  "estado_activo": true,
  "proveedor_id": ObjectId("...")
}
```

### 9.3 Estudiantes

Beneficiarios del subsidio de alimentación. Almacena datos demográficos, académicos y de vigencia del subsidio. Un estudiante puede tener múltiples registros (uno por semestre), identificados por su `codigo_estudiante`.

```json
{
  "_id": ObjectId("..."),
  "codigo_estudiante": "2021145632",
  "nombre_completo": "María Gómez",
  "correo": "maria.gomez@ucaldas.edu.co",
  "telefono": "3109876543",
  "facultad": "Ingeniería",
  "programa": "Ingeniería de Sistemas",
  "semestre": 6,
  "estrato": 2,
  "fecha_inicio_subsidio": ISODate("2026-01-20T00:00:00Z"),
  "fecha_fin_subsidio": ISODate("2026-06-15T00:00:00Z"),
  "tipo_almuerzo": "carnivoro",
  "subsidio_activo": true
}
```

### 9.4 Menús

Planificación diaria de platos por sede y tipo de comida (carnívoro o vegetariano). Embebe los datos de la sede (`nombre_sede`, `ubicacion`) para evitar joins. Incluye información nutricional, lista de ingredientes y advertencias de alérgenos.

```json
{
  "_id": ObjectId("..."),
  "sede_id": {
    "nombre_sede": "Sede Central",
    "ubicacion": "Calle 65 N 26-10, Manizales, Caldas"
  },
  "fecha": ISODate("2026-06-15T00:00:00Z"),
  "tipo_comida": "carnivoro",
  "plato": "Sancocho de gallina con papa y mazorca / Arroz blanco, bistec de res encebollado con papa al vapor",
  "info_nutricional": {
    "calorias": "650 kcal",
    "proteinas": "32g",
    "carbohidratos": "75g",
    "grasas": "18g"
  },
  "ingredientes": ["arroz", "pollo", "papa", "zanahoria", "cebolla", "tomate"],
  "advertencia_alergias": ["gluten"]
}
```

### 9.5 Consumos

Registro diario de cada ración entregada a un estudiante en una sede específica. Embebe los datos del estudiante (`nombre_completo`, `codigo_estudiante`, `tipo_almuerzo`), de la sede (`nombre_sede`, `ubicacion`) y del menú servido (`plato`, `tipo_comida`). Incluye validación de identidad.

```json
{
  "_id": ObjectId("..."),
  "estudiante_id": {
    "nombre_completo": "María Gómez",
    "codigo_estudiante": "2021145632",
    "tipo_almuerzo": "carnivoro"
  },
  "sede_id": {
    "nombre_sede": "Sede Central",
    "ubicacion": "Calle 65 N 26-10, Manizales, Caldas"
  },
  "menu_id": {
    "plato": "Sancocho de gallina con papa y mazorca / Arroz blanco, bistec de res encebollado con papa al vapor",
    "tipo_comida": "carnivoro"
  },
  "fecha_consumo": ISODate("2026-06-15T00:00:00Z"),
  "hora_ingreso": "12:30",
  "validacion_identidad": true
}
```

### 9.6 Evaluaciones

Calificaciones y retroalimentación de los estudiantes sobre la calidad del servicio y los alimentos. Embebe datos del estudiante, sede y menú para consultas offline sin joins. La calificación es un entero de 1 a 5.

```json
{
  "_id": ObjectId("..."),
  "estudiante_id": {
    "nombre_completo": "María Gómez",
    "codigo_estudiante": "2021145632",
    "semestre": 6,
    "fecha_inicio_subsidio": ISODate("2026-01-20T00:00:00Z"),
    "fecha_fin_subsidio": ISODate("2026-06-15T00:00:00Z")
  },
  "sede_id": {
    "nombre_sede": "Sede Central",
    "ubicacion": "Calle 65 N 26-10, Manizales, Caldas"
  },
  "menu_id": {
    "plato": "Sancocho de gallina con papa y mazorca / Arroz blanco, bistec de res encebollado con papa al vapor",
    "tipo_comida": "carnivoro"
  },
  "fecha_evaluacion": ISODate("2026-06-15T00:00:00Z"),
  "calificacion": 4,
  "comentario": "El plato estuvo muy bueno, bien servido y caliente.",
  "sugerencias": "Podrían agregar más variedad de jugos naturales."
}
```

---

## 10. Consultas de Usuario

Se definieron 15 consultas distribuidas en tres niveles de dificultad, según la proyección de la propuesta.

### Nivel Alto — Agregación y análisis

| Código | Consulta |
|--------|----------|
| Q1.1 | Estadística de consumo por sede |
| Q1.2 | Análisis de satisfacción por sede |
| Q1.3 | Top sedes con mayor consumo |
| Q1.4 | Estudiantes que llevan más de 30 días sin usar el beneficio |
| Q1.5 | Consumo por tipo de almuerzo |

### Nivel Medio — Filtros avanzados y arreglos

| Código | Consulta |
|--------|----------|
| Q2.1 | Filtro de consumos por sede y fecha |
| Q2.2 | Actualización de cupos de una sede |
| Q2.3 | Evaluaciones con calificación ≤ 2 |
| Q2.4 | Agregar advertencia de alergias a un menú |
| Q2.5 | Actualizar estado del subsidio de un estudiante |

### Nivel Bajo — Operaciones básicas

| Código | Consulta |
|--------|----------|
| Q3.1 | Registro de un nuevo proveedor |
| Q3.2 | Consultar menú del día por sede y fecha |
| Q3.3 | Actualizar teléfono o correo de un proveedor |
| Q3.4 | Eliminación de un consumo incorrecto o duplicado |
| Q3.5 | Conteo de estudiantes con subsidio activo |

---

## 11. Código CRUD

Operaciones básicas de creación, lectura, actualización y eliminación, junto con las operaciones sobre arreglos y filtros, correspondientes a las consultas definidas previamente.

### Nivel Medio — Filtros avanzados y arreglos

**Q2.1 — Filtro de consumos por sede y fecha**

```javascript
db.consumos.find(
  { "sede_id.nombre_sede": "Sede Central", "fecha_consumo": ISODate("2026-06-15T00:00:00Z") }
).count()
```

**Q2.2 — Actualización de cupos de una sede**

```javascript
db.sedes.updateOne(
  { _id: ObjectId("...") },
  { $set: { capacidad_maxima: 350 } }
)
```

**Q2.3 — Evaluaciones negativas (calificación ≤ 2)**

```javascript
db.evaluaciones.find(
  { calificacion: { $lte: 2 } }
)
```

**Q2.4 — Agregar advertencia de alergias a un menú**

```javascript
db.menus.updateOne(
  { _id: ObjectId("...") },
  { $push: { advertencia_alergias: "nueces" } }
)
```

**Q2.5 — Actualizar estado del subsidio de un estudiante**

```javascript
db.estudiantes.updateOne(
  { _id: ObjectId("...") },
  { $set: { subsidio_activo: false, fecha_fin_subsidio: new Date() } }
)
```

### Nivel Bajo — Operaciones básicas

**Q3.1 — Registro de un nuevo proveedor**

```javascript
db.proveedores.insertOne({
  nombre_empresa: "Nuevo Proveedor SAS",
  nit: "901234567-8",
  contacto_nombre: "Juan López",
  telefono: "3201234567",
  correo: "contacto@nuevoproveedor.com",
  frecuencia_entrega: "Quincenal",
  estado_activo: true
})
```

**Q3.2 — Consultar menú del día por sede y fecha**

```javascript
db.menus.find(
  { "sede_id.nombre_sede": "Sede Central", "fecha": ISODate("2026-06-15T00:00:00Z") }
)
```

**Q3.3 — Actualizar teléfono o correo de un proveedor**

```javascript
db.proveedores.updateOne(
  { _id: ObjectId("...") },
  { $set: { telefono: "3119876543", correo: "nuevo.correo@abc.com" } }
)
```

**Q3.4 — Eliminación de un consumo incorrecto o duplicado**

```javascript
db.consumos.deleteOne(
  { _id: ObjectId("...") }
)
```

**Q3.5 — Conteo de estudiantes con subsidio activo**

```javascript
db.estudiantes.find(
  { subsidio_activo: true }
).count()
```

---

## 12. Agregaciones de Prueba

Tuberías de agregación correspondientes a las consultas de Nivel Alto (Q1.1–Q1.5). Procesan volúmenes de datos para obtener métricas empleando operadores como `$group`, `$avg`, `$sum`, `$lookup`, `$unwind`, `$match` y `$sort`.

**Q1.1 — Estadística de consumo por sede**

```javascript
db.consumos.aggregate([
  { $group: { _id: "$sede_id.nombre_sede", total_raciones: { $sum: 1 } } },
  { $sort: { total_raciones: -1 } }
])
```

**Q1.2 — Análisis de satisfacción por sede**

```javascript
db.evaluaciones.aggregate([
  { $group: { _id: "$sede_id.nombre_sede", promedio_calificacion: { $avg: "$calificacion" } } },
  { $sort: { promedio_calificacion: -1 } }
])
```

**Q1.3 — Top sedes con mayor consumo**

```javascript
db.consumos.aggregate([
  { $group: { _id: "$sede_id.nombre_sede", total_consumos: { $sum: 1 } } },
  { $sort: { total_consumos: -1 } },
  { $limit: 3 }
])
```

**Q1.4 — Estudiantes inactivos (>30 días sin consumir)**

```javascript
var fecha_limite = new Date(new Date().setDate(new Date().getDate() - 30));
db.consumos.aggregate([
  { $group: { _id: "$estudiante_id.codigo_estudiante", ultimo_consumo: { $max: "$fecha_consumo" } } },
  { $match: { ultimo_consumo: { $lt: fecha_limite } } },
  { $sort: { ultimo_consumo: 1 } }
])
```

**Q1.5 — Consumo por tipo de almuerzo**

```javascript
db.consumos.aggregate([
  { $group: { _id: "$estudiante_id.tipo_almuerzo", total_raciones: { $sum: 1 } } }
])
```

---

## 13. Evidencias de Funcionamiento

Resultados obtenidos al ejecutar las consultas sobre el conjunto de documentos de aproximadamente **979 mil registros** (367,200 consumos + 411,833 estudiantes + 200,065 evaluaciones).

### Q1.1 — Estadística de consumo por sede

| Sede | Total raciones |
|------|---------------|
| Sede Central | 73,440 |
| Sede Palogrande | 73,440 |
| Ciencias Agropecuarias | 73,440 |
| Sede Lans | 73,440 |
| Palacio de Bellas Artes | 73,440 |

*Total: 367,200 consumos (45 por sede por día hábil, distribución uniforme)*

### Q1.2 — Análisis de satisfacción por sede

| Sede | Promedio calificación |
|------|---------------------|
| Palacio de Bellas Artes | 3.8 |
| Sede Lans | 3.8 |
| Ciencias Agropecuarias | 3.7 |
| Sede Central | 3.7 |
| Sede Palogrande | 3.7 |

*Total evaluaciones: 200,065*

### Q1.3 — Top sedes con mayor consumo

| Sede | Total consumos |
|------|--------------|
| Sede Central | 73,440 |
| Sede Palogrande | 73,440 |
| Ciencias Agropecuarias | 73,440 |

### Q1.4 — Estudiantes inactivos (>30 días sin consumir)

| Código estudiante | Último consumo |
|-------------------|---------------|
| 00000102738 | 2018-01-22 |
| 00000114464 | 2018-01-24 |
| 00000126896 | 2018-01-25 |
| 00000147548 | 2018-01-31 |
| 00000141625 | 2018-02-01 |

*Total: 43,267 estudiantes inactivos*

### Q1.5 — Consumo por tipo de almuerzo

| Tipo de almuerzo | Total raciones |
|-----------------|---------------|
| Carnívoro | 183,418 |
| Vegetariano | 183,782 |

---

### Resultados de las demás consultas

| Consulta | Resultado |
|----------|-----------|
| Q2.1 — Filtro de consumos por sede y fecha | 45 consumos (Sede Central, 2026-06-15) |
| Q2.2 — Actualización de cupos de una sede | 1 modificado (capacidad: 300 → 350) |
| Q2.3 — Evaluaciones negativas (calificación ≤ 2) | 30,012 evaluaciones |
| Q2.4 — Agregar advertencia de alergias a un menú | 1 modificado (alergia "nueces" añadida) |
| Q2.5 — Actualizar estado del subsidio | 1 modificado (subsidio desactivado) |
| Q3.1 — Registro de un nuevo proveedor | 1 insertado |
| Q3.2 — Consultar menú del día por sede y fecha | 2 menús (carnívoro + vegetariano) |
| Q3.3 — Actualizar teléfono o correo de un proveedor | 1 modificado |
| Q3.4 — Eliminación de un consumo incorrecto | 1 eliminado |
| Q3.5 — Conteo de estudiantes con subsidio activo | 5,631 estudiantes con subsidio activo |

---

## 14. Conexión Front-End

Para la capa visual se empleó **Streamlit**, una herramienta Python orientada a la creación rápida de dashboards y paneles de gestión. La comunicación con la base de datos se realiza a través del controlador **PyMongo**, que envía las operaciones directamente a MongoDB Atlas sin necesidad de una API intermedia. Está pensada para que personal administrativo y de bienestar universitario pueda operar el sistema sin conocimientos técnicos.

El panel principal se compone de **seis módulos** accesibles desde una barra lateral:

- **Proveedores**: muestra total de empresas, estado activo/inactivo y permite administrar sus datos de contacto y frecuencia de entrega.
- **Sedes**: despliega la capacidad máxima de cada comedor, su ubicación y horarios, con opciones de edición.
- **Estudiantes**: incluye un buscador por código y filtro por semestre para localizar beneficiarios del subsidio, además de indicadores de vigencia.
- **Consumos**: registra las raciones servidas cada día, valida identidad y muestra estadísticas del día actual.
- **Menús**: organiza los platos por tipo de comida y sede, con detalle nutricional y advertencias de alérgenos.
- **Evaluaciones**: consolida las calificaciones de los estudiantes y muestra el promedio por sede, junto con los comentarios recibidos.

Cada módulo despliega tarjetas resumen con cifras clave, una tabla con paginación de 20 filas y un botón para crear nuevos registros. Las operaciones de modificación y borrado se disparan desde íconos en la misma fila de la tabla; las eliminaciones solicitan confirmación mediante un cuadro de diálogo. El intercambio de datos sigue esta ruta:

```
Streamlit → Service (capa lógica) → PyMongo → MongoDB Atlas
                                      ↓
                              Modelo from_dict() → Renderizado
```

Los estulos aplican una combinación de colores institucional (azul marino #0B2545 y dorado #C9A227), con las fuentes Source Serif 4 para encabezados, Inter para cuerpo de texto e iconos de Font Awesome para las tarjetas y acciones.

---

## 15. Conclusiones y Mejoras Futuras

### 15.1 Conclusiones

1. **Modelo NoSQL efectivo**: La estrategia híbrida de documentos embebidos con referencias extendidas permitió representar las relaciones del negocio sin necesidad de joins complejos, mejorando el rendimiento de las consultas más frecuentes.

2. **Cobertura funcional completa**: El sistema cubre el ciclo completo de gestión del subsidio: desde la contratación de proveedores hasta la evaluación de la calidad del servicio por parte de los estudiantes.

3. **Interfaz intuitiva**: Streamlit permitió desarrollar una interfaz moderna y funcional en Python puro, eliminando la necesidad de un frontend separado con JavaScript.

4. **Validación de datos robusta**: El uso de `$jsonSchema` de MongoDB y la definición de modelos Python garantizan la integridad de los datos en todos los niveles.

5. **Volumen de datos de prueba**: Se generaron conjuntos de datos realistas (50,000+ estudiantes, 100,000+ consumos, 15,000+ menús) que permiten validar el rendimiento del sistema bajo carga.

### 15.2 Mejoras Futuras

1. **Unificar codigo_estudiante como llave única**: Agregar un índice único sobre `codigo_estudiante` en la colección `estudiantes` para evitar que un mismo estudiante tenga registros duplicados.

2. **Agregar facultad al documento embebido de consumos**: Incluir el campo `facultad` dentro de `consumo.estudiante_id` para poder consultar el top de facultades consumidoras sin necesidad de `$lookup`.

3. **Separar proveedores como colección embebida en sedes**: Mover los datos del proveedor como documento embebido dentro de `sedes` en lugar de usar una referencia por ObjectId, eliminando la necesidad de la colección `proveedores` por separado.

4. **Campo calculado de edad del subsidio**: Agregar un campo `dias_restantes` en `estudiantes` que indique cuántos días faltan para que venza su subsidio, actualizado periódicamente.

5. **Normalizar tipo_almuerzo**: Crear una colección independiente `tipos_comida` con los valores permitidos (carnívoro, vegetariano, especial) y referenciarlos por código en lugar de usar strings literales.

6. **Bitácora de cambios**: Agregar un campo `historial_cambios` (arreglo de objetos) en cada colección para registrar quién y cuándo modificó cada documento.
