# Foundry_AI Docker Setup

Este proyecto permite ejecutar un agente de Azure AI Foundry desde un contenedor Docker, con chat interactivo en la terminal.

## Archivos del proyecto
- `Foundry_AI.py` - Script Python para chat interactivo con el agente Azure AI
- `Dockerfile` - Imagen Docker basada en `python:3.11-slim` con dependencias Azure
- `requirements.txt` - Paquetes Python (azure-identity, azure-ai-projects, azure-ai-agents, requests)
- `.dockerignore` - Archivos excluidos del contexto de Docker
- `.env` - Variables de entorno con credenciales Azure AD (no subir a repositorios públicos)

## Requisitos previos
- Docker Desktop instalado y en ejecución
- Cuenta de Azure con acceso al recurso Azure AI Foundry
- Azure Active Directory App Registration con permisos

---

## Paso a paso: Setup completo

### 1. Crear Azure AD App Registration

1. Ve al **Azure Portal** (portal.azure.com)
2. Navega a **Azure Active Directory** → **App registrations**
3. Haz clic en **+ New registration**
4. Configura:
   - **Name**: Foundry-AI-App (o el nombre que prefieras)
   - **Supported account types**: Single tenant
   - Haz clic en **Register**
5. Copia y guarda:
   - **Application (client) ID**
   - **Directory (tenant) ID**

### 2. Crear Client Secret

1. En tu App Registration, ve a **Certificates & secrets**
2. Haz clic en **+ New client secret**
3. Configura:
   - **Description**: Docker App Secret
   - **Expires**: 24 months (o el tiempo que prefieras)
4. Haz clic en **Add**
5. **IMPORTANTE**: Copia el **Value** del secret INMEDIATAMENTE (solo se muestra una vez)
   - ⚠️ NO copies el "Secret ID", copia el "Value"

### 3. Asignar permisos al Service Principal

**Opción A: Desde Azure Cloud Shell (recomendado)**

1. Abre **Cloud Shell** en el portal Azure (icono `>_` en la barra superior)
2. Ejecuta estos comandos (reemplaza los valores):

```bash
# Variables (reemplaza con tus valores)
APP_ID="<tu-application-client-id>"
RESOURCE_GROUP="<tu-resource-group>"  # Ej: AzureFoundry-Grado-Master
RESOURCE_NAME="<nombre-recurso-foundry>"  # Ej: foundryproject-tecnun-resource
SUBSCRIPTION_ID="<tu-subscription-id>"

# Construir el Resource ID
RESOURCE_ID="/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/$RESOURCE_NAME"

# Asignar el rol Cognitive Services User
az role assignment create \
  --assignee "$APP_ID" \
  --role "Cognitive Services User" \
  --scope "$RESOURCE_ID"
```

**Opción B: Desde el Portal Azure**

1. Ve a tu recurso Azure AI Foundry en el portal
2. Selecciona **Access control (IAM)** en el menú izquierdo
3. Haz clic en **+ Add** → **Add role assignment**
4. En la pestaña **Role**:
   - Busca y selecciona **Cognitive Services User**
   - Haz clic en **Next**
5. En la pestaña **Members**:
   - Selecciona **User, group, or service principal**
   - Haz clic en **+ Select members**
   - Busca tu Application (client) ID o nombre de app
   - Selecciónala y haz clic en **Select**
6. Haz clic en **Review + assign** dos veces

### 4. Configurar el archivo .env

Crea o edita el archivo `.env` en la carpeta del proyecto con tus credenciales:

```env
# Credenciales Azure AD (OBLIGATORIO)
AZURE_CLIENT_ID=<tu-application-client-id>
AZURE_TENANT_ID=<tu-directory-tenant-id>
AZURE_CLIENT_SECRET=<tu-client-secret-value>

# Opcional: API Key (no funciona con este servicio, usa Azure AD)
# FOUNDRY_API_KEY=<tu-api-key>
```

**⚠️ IMPORTANTE**: 
- No subas el archivo `.env` a repositorios públicos (ya está en `.gitignore`)
- Usa el **Value** del secret, NO el Secret ID

### 5. Construir la imagen Docker

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
docker build -t foundry-ai .
```

Esto tomará 1-2 minutos la primera vez (descarga la imagen base e instala dependencias).

### 6. Ejecutar el contenedor y chatear con el agente

```powershell
docker run --rm -it --env-file .env foundry-ai
```

**Salida esperada:**
```
Using ClientSecretCredential
Connecting to: https://...
Connected to agent: asst_l7K5YHdGNfxlERMhAmwzDuhv

Thread: thread_xxxxx
=== Chat (escribe 'exit' para salir) ===

You: 
```

Escribe tus mensajes y el agente responderá. Para salir, escribe `exit` o presiona `Ctrl+C`.

---

## Solución de problemas

### Error: "Invalid client secret provided"
- **Causa**: Usaste el Secret ID en lugar del Secret Value
- **Solución**: Crea un nuevo client secret en Azure Portal y copia el **Value** (no el ID)

### Error: "PermissionDenied" o "lacks the required data action"
- **Causa**: El Service Principal no tiene permisos en el recurso
- **Solución**: Asigna el rol "Cognitive Services User" siguiendo el Paso 3

### Error: "Resource group not found"
- **Causa**: Nombre del Resource Group incorrecto
- **Solución**: Verifica el nombre en el portal o ejecuta:
  ```bash
  az cognitiveservices account list --query "[].{Name:name, RG:resourceGroup}" -o table
  ```

### Error: "Docker daemon is not running"
- **Causa**: Docker Desktop no está iniciado
- **Solución**: Inicia Docker Desktop y espera a que esté completamente activo

### Error: "Authentication failed" o "DefaultAzureCredential failed"
- **Causa**: El `.env` no tiene las credenciales correctas o está mal formado
- **Solución**: Verifica que el `.env` tenga las 3 variables sin espacios extra:
  ```
  AZURE_CLIENT_ID=abc123...
  AZURE_TENANT_ID=def456...
  AZURE_CLIENT_SECRET=ghi789...
  ```

---

## Comandos útiles

### Ver logs del contenedor si falla
```powershell
docker run --rm --env-file .env foundry-ai
```

### Reconstruir la imagen tras cambios en el código
```powershell
docker build -t foundry-ai . --no-cache
```

### Verificar que la imagen existe
```powershell
docker images foundry-ai
```

### Ejecutar sin modo interactivo (para testing)
```powershell
docker run --rm --env-file .env foundry-ai
```

---

## Notas de seguridad

- ✅ El archivo `.env` está en `.gitignore` por defecto
- ✅ Usa `--rm` al ejecutar el contenedor para limpieza automática
- ✅ Los secretos nunca se imprimen en logs
- ⚠️ No compartas tu Client Secret en capturas de pantalla o logs públicos
- ⚠️ Rota los secrets periódicamente desde Azure Portal

---

## Arquitectura

```
┌─────────────┐
│   Docker    │
│  Container  │
│             │
│ Python 3.11 │
│   + Azure   │
│     SDK     │
└──────┬──────┘
       │
       │ HTTPS + OAuth Token
       │ (ClientSecretCredential)
       ↓
┌─────────────────────────┐
│  Azure AI Foundry API   │
│  (Agents Service)       │
└─────────────────────────┘
```

---

## Autor

MADI - M.Britez - Proyecto Cloud Computing
