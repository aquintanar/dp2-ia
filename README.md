# dp2-ia

Este es el backend de la IA que desarrollamos.

## Despliegue

Primero hay que clonar el repositorio.

```sh
git clone https://github.com/aquintanar/dp2-ia.git
cd dp2-ia
```

Para desplegar el sistema se debe correr el siguiente script, introduciendo la direccion url base a la cual se deplegará el sitio web. Por ejemplo:

```sh
chmod +x deploy.sh
./deploy.sh http://3.218.68.113
```

El script de bash manejará toda la logica necesaria de despliegue.