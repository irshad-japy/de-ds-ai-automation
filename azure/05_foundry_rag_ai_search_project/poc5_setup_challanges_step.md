q1. i want to complete this below steps how to create foundry project

i want to complete this below steps how to create foundry project



## 5. Create Microsoft Foundry project/resource



Use the Microsoft Foundry portal at `https://ai.azure.com`.



1. Sign in with the Azure account connected to your subscription.

2. Make sure you are using **New Foundry** if the UI offers a toggle.

3. Select the current project name in the upper-left area.

4. Select **Create new project**.

5. Project name: `poc05-rag-project`.

6. Open **Advanced options** if shown.

7. Select resource group `rg-poc05-foundry-rag`.

8. Select your chosen location.

9. Create the project.

10. Wait until resource creation finishes.



The portal creates/uses a Foundry resource under the project. Keep the Foundry resource and project in the same resource group for this POC when possible.



### Verification



Inside the Foundry project:



- project opens successfully;

- resource status is healthy;

- you can open the Models area.



--- 

Before launching into the portal, ensure your subscription has the Microsoft.CognitiveServices and Microsoft.MachineLearningServices resource providers registered, and that your user role has at least Contributor or Azure AI Developer permissions on the resource group rg-poc05-foundry-rag.

Step-by-Step Setup Guide
1
Navigate and Authenticate
Prerequisite: Valid Azure Tenant Access
Open a browser and navigate to ai.azure.com.

Click Sign in in the top right.

Select the organizational account attached to your target Azure subscription.

If prompted with a tenant/directory picker, switch to the tenant hosting your resource group.

2
Verify UI Mode and Open Switcher
Look for a banner or toggle in the upper ribbon indicating New Foundry (or "Try the new Azure AI Studio/Foundry"). Ensure it is active.

Click the workspace/project breadcrumb or dropdown in the upper-left navigation area.

Click + New project (or Create new project).

3
Enter Basic Project Details
Set the Project name to:

Plaintext
poc05-rag-project
Review the auto-generated hub name. If the UI does not display underlying resource fields directly on the main card, click Customize or Advanced options.

4
Configure Foundry Resource and Region
Critical for RAG quota and model availability
Resource group: From the dropdown, select:

Plaintext
rg-poc05-foundry-rag
(If it does not exist yet, select "Create new" and enter that exact name).
2. Foundry resource (Hub): Select an existing Foundry resource in that resource group or choose Create a new resource (naming it something like foundry-hub-poc05).
3. Location / Region: Select a region with wide capacity for both LLMs and embeddings (e.g., East US 2, Sweden Central, or West US 3).

5
Provision and Wait for Completion
Click Create (or Review + create -> Create).

The portal will display an initialization panel ("Creating project...").

Keep the tab open while Azure creates the AI Hub, key vault, storage account, and project bindings. This typically takes 1 to 3 minutes.

Post-Creation Verification
Once redirected into the new project workspace, run through these validation checks:

Project Navigation: Verify the breadcrumb in the top-left displays poc05-rag-project.

Resource Health:

Click Management Center (gear/settings icon at the bottom-left navigation bar).

Select Overview and ensure the linked AI Hub shows a status of Active and points to rg-poc05-foundry-rag.

Model Catalog Availability:

Return to the project view and click Models + endpoints (or Model catalog) in the left menu.

Search for text-embedding-3-small or gpt-4o to confirm the model catalog opens without permission warnings or tenant connectivity errors.

Want instructions for deploying your embedding and chat models next?

Yes
i get this its correct

Yes, this is the correct screen. In the updated Foundry portal, creating a new Foundry resource automatically provisions your first project alongside it.

Fill out the fields on this screen as follows:

Subscription: Keep Azure subscription 1 (or select the subscription you intend to use).

Resource group:

Select rg-poc05-foundry-rag from the dropdown.

If it is not listed, click Create new right below the box, type rg-poc05-foundry-rag, and click OK.

Name: Enter a name for the parent Foundry resource (Hub), such as:

Plaintext
foundry-hub-poc05
(This names the underlying Azure AI resource that manages compute, connections, and storage).

Region: Keep (US) East US (or choose another region like (US) East US 2 or (Europe) Sweden Central if you need higher quota for specific models).

Your first project:

Scroll down to the bottom section visible in your screenshot.

In the project name field, enter:

Plaintext
poc05-rag-project
Deploy:

Click the blue Review + create button at the bottom (the default Storage, Networking, and Identity settings are sufficient for this POC).

Review the validation summary, then click Create.

Wait 1–3 minutes while Azure provisions the resources and opens your new project workspace.

now i have created now i want to follow step 6 so please guide me





## 6. Deploy the chat model



In Microsoft Foundry:



1. Select **Discover** → **Models**.

2. Search for a small chat model available in your subscription/region.

3. Open the model card.

4. Select **Deploy**.

5. Use **Default settings** for a beginner POC unless you need custom quota settings.

6. Set deployment name to something easy, for example:



```text

rag-chat

```



7. Deploy.

8. Wait for provisioning state **Succeeded**.

9. Open the playground and send a tiny test question such as `Say hello in one sentence.`



### Verification



You must receive a model response in the playground.



> Important: application code calls the **deployment name**, not necessarily the underlying model name.

Follow these steps directly from your current screen to deploy the chat model:

1. Open the Model Catalog
Click Discover in the top navigation bar (or click the Explore models card at the bottom of your screen).

In the left menu, select Models.

Quick check: If you intended to work strictly inside poc05-rag-project, notice the breadcrumb in your top-left says proj-default. Click that dropdown if you want to switch to poc05-rag-project before deploying (though both share the same underlying Azure OpenAI endpoint shown on your screen).

2. Find and Select the Model
In the search box at the top of the model catalog, search for:

Plaintext
gpt-4o-mini
(This is the recommended low-cost, small chat model for RAG POCs in Azure Foundry).

Click the gpt-4o-mini card to open its detail page.

3. Deploy the Model
Click the blue Deploy button.

Choose Default settings (or select Deploy if it doesn't prompt for advanced settings).

In the configuration dialog, find the Deployment name field, erase the auto-populated name, and enter exactly:

Plaintext
rag-chat
Leave the remaining deployment type (Global Standard / Standard) and quota at their defaults.

Click Deploy.

4. Wait for Provisioning
Keep the page open while Azure initializes the deployment.

Wait until the status displays Succeeded (usually 30 to 90 seconds).

5. Verification in the Playground
Click Open in playground (or navigate to Operate / Build → Playground).

Verify that the Deployment dropdown at the top of the playground is set to rag-chat.

In the chat message box, send:

Plaintext
Say hello in one sentence.
Confirm you receive a coherent text response back from the model.

i try to deploy gpt-4o-mini getting this page warning so please guide me

The "Deprecated model" warning indicates that version 2024-07-18 has entered Microsoft's retirement schedule. For a proof of concept (POC), this is not a blocker, and you can still proceed or select a newer model.

Option 1: Continue with this model (Recommended for your POC)
Deprecated models remain functional until their final retirement date. For learning and rapid testing, you can deploy it directly:

Click Default settings from the dropdown menu currently open on your screen.

In the deployment popup that appears:

Change the Deployment name to:

Plaintext
rag-chat
Leave the remaining settings at default.

Click Deploy.

Once the status shows Succeeded, proceed to the playground and send your test prompt: Say hello in one sentence.

Option 2: Check for a newer version or alternate model
To avoid using a deprecated version:

Check for an updated version: Click the dropdown next to Version: 2024-07-18 (to the left of the purple Deploy button). If a newer version is listed, select it to clear the warning.

Choose an alternative model: If no newer version is listed or deployment fails due to regional restrictions, return to Discover → Models and pick another chat model, such as:

gpt-4o (version 2024-11-20 or newer)

gpt-4.1-mini (if available in your selected region)

Note on Project Scope: Notice in the top-left breadcrumb bar that your current active project is proj-default. If you want this deployment linked to the poc05-rag-project you configured in Step 5, click the proj-default ⬍ dropdown and switch to poc05-rag-project before clicking deploy.

i am not able to click default setting after use custome setting its not able to deploy so can i use free model like cohere

The issue preventing deployment is Insufficient quota. Your Azure subscription currently has 0 Tokens Per Minute (TPM) assigned for regional Standard deployment of this model in East US.

Solution 1: Switch to "Global Standard" (Try this first)
In most Azure subscriptions, regional Standard has zero default quota, but Global Standard has available quota.

In the right-hand panel, click the Deployment type dropdown (currently showing Standard).

Select Global Standard (or DataZone Standard).

Check if the "Insufficient quota" warning disappears and the Deploy button turns blue.

If it turns blue:

Change the Deployment name from gpt-4o-mini to:

Plaintext
rag-chat
Click Deploy.

Solution 2: Can you use Cohere or another model?
Yes, absolutely. The instructions specify:

"Search for a small chat model available in your subscription/region... Set deployment name to rag-chat."

Because application code connects to the deployment name (rag-chat), you can substitute an alternative model.

Option A: Cohere Command
Close the right drawer (click ✕).

Go back to Discover → Models.

In the search box, search for:

Plaintext
Cohere Command R
Click the model card and select Deploy → choose the Serverless API (Pay-as-you-go) option.

Accept the Marketplace terms if prompted.

Set the Deployment name to:

Plaintext
rag-chat
Click Deploy.

Option B: Microsoft Phi-3.5 or Phi-4 (Recommended alternative)
If you want a lightweight chat model that doesn't require third-party marketplace terms:

Search the model catalog for:

Plaintext
Phi-3.5-mini-instruct
Click Deploy (Serverless API).

Set the Deployment name to rag-chat and click Deploy.

Once Deployed (Step 8 & 9)
Whichever model you deploy:

Wait for the status to show Succeeded.

Click Open in playground.

Send the verification prompt:

Plaintext
Say hello in one sentence.
Confirm the model replies back.

i try both but still not able to deploy it

Select Global Standard (or DataZone Standard).



i try to deploy cohere model then i need projects

This screen is offering the solution: your original project is in eastus, where your subscription has zero quota for chat models. The portal is offering to automatically create a new project in East US 2, where quota and capacity are available.

Complete the deployment directly from this popup by following these steps:

1. Fill out the "Select another project" dialog
Available regions: Keep East US 2 selected.

Project name: Change erirshad26-6388 to a descriptive name:

Plaintext
poc05-rag-project-eastus2
Advanced options:

Click > Advanced options to expand it.

Make sure the Resource group is set to rg-poc05-foundry-rag (so all your POC assets stay in the same resource group).

Click the purple Continue button.

2. Complete Model Deployment
Once Azure provisions the workspace in East US 2, the deployment configuration panel will open:

In the Deployment name field, replace the default text and enter:

Plaintext
rag-chat
Leave the deployment SKU/type at default.

Click Deploy.

Wait 30–60 seconds for the status to switch to Succeeded.

3. Verify in Playground
Click Open in playground (or navigate to Operate → Playground).

Ensure the model dropdown is set to rag-chat.

Submit the verification prompt:

Plaintext
Say hello in one sentence.
Confirm you get an answer back from the model.

now i getting error after deploy button click so please guide me

This error occurs because Cohere Command A requires a dedicated serverless Marketplace offering and cannot be deployed through the direct account deployment method in this resource.

Now that your active project is in East US 2 (poc05-rag-project-eastus2), you can deploy gpt-4o-mini, which has available quota in this region.

Step-by-step: Deploy gpt-4o-mini in East US 2
Return to the Model Catalog:

In the left sidebar, click Models (under Discover).

Select gpt-4o-mini:

Search for gpt-4o-mini in the search bar and open its card.

Open Deployment Settings:

Click the purple Deploy button.

If a menu drops down, select Custom settings (or Default settings if it proceeds directly).

Configure the Deployment:

Deployment name: Erase the default and type:

Plaintext
rag-chat
Deployment type: Select Global Standard (if you used Custom settings).

Model version: Keep the latest/default available.

Deploy:

Click Deploy at the bottom right.

Wait 30–60 seconds for the deployment state to show Succeeded.

Fallback if gpt-4o-mini shows any restriction
If gpt-4o-mini still shows a regional limitation in your subscription:

Search the catalog for Phi-3.5-mini-instruct or Phi-4 (Microsoft's direct native models).

Click Deploy.

Set the Deployment name to rag-chat and click Deploy.

Test in the Playground
After deployment completes, click Open in playground (or navigate to Operate → Playground).

Ensure the deployment selector at the top is set to rag-chat.

In the message box, send:

Plaintext
Say hello in one sentence.
Verify that the assistant returns a response.

still not working so please guide me how to use another model

The issue occurs because:

Third-party models (like Cohere) require marketplace subscription billing and cannot be deployed through a direct account deployment (DeploymentModelNotSupported).

New Azure subscriptions often have 0 quota for certain models or regional deployment types (Standard), but have available capacity under Global Standard or for Microsoft-native models.

You are currently inside poc05-rag-project-eastus2. To deploy a working chat model under the name rag-chat, use one of the following two options.

Option 1: Deploy Microsoft Phi-3.5-mini-instruct (Fastest & Free of Marketplace Errors)
Microsoft’s own Phi models avoid third-party marketplace restrictions and work for POC chat and RAG tasks.

In the left menu, click Models (under Discover).

In the search bar at the top, type:

Plaintext
Phi-3.5-mini-instruct
Click on the Phi-3.5-mini-instruct card.

Click the purple Deploy button.

In the configuration window:

Deployment name: Replace the default text and enter:

Plaintext
rag-chat
Keep the deployment SKU / type at its default.

Click Deploy.

Wait 30–60 seconds until the status shows Succeeded.

Option 2: Check your exact model quota before deploying
To confirm which models have available capacity in your subscription rather than guessing:

Click Manage in the top navigation bar (near Discover, Build, Operate).

In the left menu under Management, select Quota (or Usage + quotas).

Look down the list for any model that shows Available Quota > 0 (e.g., gpt-4o-mini, gpt-35-turbo, or Phi-3.5).

Note the Deployment type where quota is available (usually GlobalStandard).

Return to Discover → Models, search for that specific model:

Click Deploy → Custom settings.

Set Deployment name to rag-chat.

Set Deployment type to Global Standard.

Click Deploy.

Verification (Playground Test)
Once the deployment status reaches Succeeded:

Click Open in playground (or click Operate → Playground in the top navigation).

Verify the top deployment dropdown shows rag-chat.

Type:

Plaintext
Say hello in one sentence.
Press Enter. A reply from the model confirms Step 6 is complete.

its getting this now i want to follow next step is

i attach readme.md file in this have all the step to complete this pocs i attach full zip file



## 7. Deploy the embedding model



Repeat the model deployment flow for an embedding model.



Recommended when available:



```text

text-embedding-3-small

```



Use deployment name:



```text

rag-embedding

```



If you use `text-embedding-3-small` with its default output size, set:



```text

EMBEDDING_DIMENSIONS=1536

```



If you use a different embedding model or explicitly choose another dimensions value, change `EMBEDDING_DIMENSIONS` to match the actual vector size.



### Verification



Confirm the embedding deployment status is **Succeeded**.



---

Step 1: Navigate to the Model Catalog
From your current screen in poc05-rag-project-eastus2:

In the top navigation bar, click Discover (located between Home and Build).

In the left sidebar under Discover, click Models.

Step 2: Find text-embedding-3-small
In the search box at the top, type:

Plaintext
text-embedding-3-small
Click on the text-embedding-3-small card to open its detail page.

Step 3: Deploy the Embedding Model
Click the purple Deploy button in the top right.

If a dropdown menu opens, choose Default settings first.

If it indicates insufficient quota (like earlier), choose Custom settings and switch the Deployment type to Global Standard.

Set the Deployment name field to exactly:

Plaintext
rag-embedding
Leave the remaining version and rate-limit settings at default.

Click Deploy.

Step 4: Verification
Once the deployment initializes, go to Operate (top menu) → Deployments (or Models + endpoints).

Look for rag-embedding in your deployments list.

Confirm the Provisioning state reads Succeeded.

Step 5: Update Your .env File
Open .env inside your extracted project folder (POC_05_FOUNDRY_RAG_AI_SEARCH_PROJECT) and update the deployment variables:

Code snippet
# Chat deployment from Step 6 (use the exact name you gave it in Foundry)
AZURE_OPENAI_CHAT_DEPLOYMENT=rag-chat

# Embedding deployment from Step 7
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=rag-embedding
EMBEDDING_DIMENSIONS=1536
Note on your Chat Model: In your screenshot, you deployed Phi-4-mini-instruct. If you kept its default deployment name instead of naming it rag-chat, set AZURE_OPENAI_CHAT_DEPLOYMENT=Phi-4-mini-instruct in your .env file, because your Python code calls the deployment name, not the model name.

after deploy i getting this

The deployment succeeded (Provisioning state: Succeeded).

Before moving to the next step, make note of the following values shown on your screen:

1. Important Note on Deployment Names
The default names were kept instead of custom aliases:

Embedding Deployment Name: text-embedding-3-small

Chat Deployment Name: Phi-4-mini-instruct (from Step 6)

When configuring your project's .env file, map the variables to these exact names:

Code snippet
AZURE_OPENAI_CHAT_DEPLOYMENT=Phi-4-mini-instruct
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
2. Copy Your Credentials
From the Details screen currently open:

Click the copy icon next to Endpoint:

Plaintext
https://poc05-rag-project-eastu-resource.services.ai.azure.com
Click the copy icon next to Key to copy your API key.

Save both values for your .env configuration (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY).

Next Step: Step 8 (Azure AI Search Service)
In standard Foundry RAG setups, Step 8 provisions the Azure AI Search vector database.

If Step 8 in your README.md is Create Azure AI Search Service:

Open the Azure Portal.

Search for AI Search (or Azure AI Search) in the top search bar and click Create.

Resource Group: Select rg-poc05-foundry-rag.

Service Name: Enter something identifiable like search-poc05-rag.

Location: Select East US 2 (matching your Foundry resource).

Pricing Tier: Select Basic or Free (Free is sufficient for small POCs; Basic supports semantic ranker).

Click Review + Create → Create.

Paste the text of Step 8 from your README.md if you would like step-by-step guidance tailored to its exact requirements.

before going to next step 8 please i want to all .env value



please guide me to get or retrieve each value below is the full details which i need



# ---------- Azure AI Search ----------

# key = simplest first run; entra = DefaultAzureCredential / az login

SEARCH_AUTH_MODE=key

AZURE_SEARCH_ENDPOINT=https://YOUR-SEARCH-SERVICE.search.windows.net

AZURE_SEARCH_ADMIN_KEY=PASTE_LOCAL_KEY_HERE

AZURE_SEARCH_INDEX_NAME=poc05-rag-index



# ---------- Microsoft Foundry / OpenAI-compatible v1 endpoint ----------

# Copy the exact inference base URL exposed by your Foundry resource.

# It usually ends with /openai/v1/

FOUNDRY_AUTH_MODE=key

FOUNDRY_OPENAI_BASE_URL=https://YOUR-FOUNDRY-RESOURCE.openai.azure.com/openai/v1/

FOUNDRY_API_KEY=PASTE_LOCAL_KEY_HERE

FOUNDRY_CHAT_DEPLOYMENT=rag-chat

FOUNDRY_EMBEDDING_DEPLOYMENT=rag-embedding



# Must exactly match the embedding length stored in Azure AI Search.

EMBEDDING_DIMENSIONS=1536



# If true, pass dimensions=EMBEDDING_DIMENSIONS to the embeddings request.

# text-embedding-3-* supports configurable dimensions. Set false for models that do not.

EMBEDDING_REQUEST_DIMENSIONS=false



# ---------- RAG behavior ----------

CHUNK_SIZE_TOKENS=300

CHUNK_OVERLAP_TOKENS=50

TOP_K=5

MAX_OUTPUT_TOKENS=500



# ---------- Optional observability ----------

APPLICATIONINSIGHTS_CONNECTION_STRING=



# ---------- Optional logging ----------

LOG_LEVEL=INFO

Here is the exact breakdown of how to retrieve and set each value in your .env file based on the resources you just deployed.

1. Values You Can Fill In Right Now (Foundry & Deployments)
These come directly from the deployments visible in your previous two screenshots.

Variable	Value to Enter	Where to Find It
FOUNDRY_AUTH_MODE	key	Keep default.
FOUNDRY_OPENAI_BASE_URL	[https://poc05-rag-project-eastu-resource.services.ai.azure.com/openai/v1/](https://poc05-rag-project-eastu-resource.services.ai.azure.com/openai/v1/)	Look at the Endpoint field in your last screenshot. Copy that URL and append /openai/v1/ to the end. (Alternatively, click Home in the top bar and copy the pre-formatted Azure OpenAI endpoint card).
FOUNDRY_API_KEY	(Your copied key)	On your current screen (under the Key heading with black dots), click the copy icon on the far right.
FOUNDRY_CHAT_DEPLOYMENT	Phi-4-mini-instruct	This is the deployment name of the model you deployed in Step 6 (visible in your playground screenshot).
FOUNDRY_EMBEDDING_DEPLOYMENT	text-embedding-3-small	This is the deployment name visible in the Name field under Deployment info in your latest screenshot.
EMBEDDING_DIMENSIONS	1536	
text-embedding-3-small outputs 1,536-dimensional vectors by default.  
ZIP

EMBEDDING_REQUEST_DIMENSIONS	false	
Keep false.  
ZIP

2. Values for Azure AI Search (Completed in Step 8)
You have not created the Search service yet—these values will be generated when you execute Step 8 in the Azure Portal:

Variable	How to Retrieve
SEARCH_AUTH_MODE	
Keep key.  
ZIP

AZURE_SEARCH_ENDPOINT	
After creating the Search service in Step 8, open the service in the Azure Portal -> go to Overview -> copy the Url field (e.g., https://<your-service-name>.search.windows.net).  
ZIP

AZURE_SEARCH_ADMIN_KEY	
In Azure Portal -> your AI Search service -> left menu under Settings -> select Keys -> copy the Primary admin key.  
ZIP

AZURE_SEARCH_INDEX_NAME	
Leave as poc05-rag-index (your ingestion script will create an index with this name).  
ZIP

3. Static & Optional Defaults
Leave these at their provided defaults:

Variable	Value	Description
CHUNK_SIZE_TOKENS	300	
Target token length per text chunk.  
ZIP

CHUNK_OVERLAP_TOKENS	50	
Overlap between chunks for continuity.  
ZIP

TOP_K	5	
Number of document chunks retrieved per query.  
ZIP

MAX_OUTPUT_TOKENS	500	
Generation ceiling for model answers.  
ZIP

APPLICATIONINSIGHTS_CONNECTION_STRING	(Leave empty)	
Optional telemetry; not required for the POC.  
ZIP

LOG_LEVEL	INFO	
Console logging level.  
ZIP

Complete .env Template to Copy and Save
Save this into your .env file (replacing the placeholder values for the key and search service):

Code snippet
# ---------- Azure AI Search ----------
SEARCH_AUTH_MODE=key
AZURE_SEARCH_ENDPOINT=https://YOUR-SEARCH-SERVICE.search.windows.net
AZURE_SEARCH_ADMIN_KEY=YOUR_SEARCH_ADMIN_KEY_FROM_STEP_8
AZURE_SEARCH_INDEX_NAME=poc05-rag-index

# ---------- Microsoft Foundry / OpenAI-compatible v1 endpoint ----------
FOUNDRY_AUTH_MODE=key
FOUNDRY_OPENAI_BASE_URL=https://poc05-rag-project-eastu-resource.services.ai.azure.com/openai/v1/
FOUNDRY_API_KEY=PASTE_COPIED_KEY_HERE
FOUNDRY_CHAT_DEPLOYMENT=Phi-4-mini-instruct
FOUNDRY_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Must exactly match the embedding length stored in Azure AI Search.
EMBEDDING_DIMENSIONS=1536
EMBEDDING_REQUEST_DIMENSIONS=false

# ---------- RAG behavior ----------
CHUNK_SIZE_TOKENS=300
CHUNK_OVERLAP_TOKENS=50
TOP_K=5
MAX_OUTPUT_TOKENS=500

# ---------- Optional observability ----------
APPLICATIONINSIGHTS_CONNECTION_STRING=

# ---------- Optional logging ----------
LOG_LEVEL=INFO
ok please guide me to create step 8

Step 8: Create Azure AI Search Service
Execute this step in the standard Azure Portal rather than the Foundry portal to configure the search service, tier, and access keys[cite: 1].

1. Provision the Search Service
Open a browser tab and navigate to portal.azure.com.

In the top global search bar, type Azure AI Search and select Azure AI Search from the services list.

Click + Create (or Create search service).

On the Basics tab, configure the following fields:

Subscription: Select Azure subscription 1 (the same subscription hosting your Foundry project).

Resource group: Select rg-poc05-foundry-rag.

Service name: Enter a unique name in lowercase letters and numbers (e.g., search-poc05-rag-irshad).

Location: Select East US 2 (match the region of your active poc05-rag-project-eastus2 project to keep latency minimal and prevent cross-region network egress charges).

Pricing tier: Click Change Pricing Tier. Select Basic (preferred for RAG PoCs, as it supports Semantic Ranker and vector storage) or Free (sufficient for simple vector search if Basic is unavailable).

Leave the remaining tabs (Scale, Networking, Tags) at their default values.

Click Review + create, then click Create.

Wait 1 to 2 minutes until the deployment status shows Your deployment is complete.

2. Retrieve the Search Endpoint and Admin Key
Click Go to resource from the completion screen (or open your newly created search service from the Azure Portal).

On the Overview page, locate the Url field in the top-right metadata card (e.g., [https://search-poc05-rag-irshad.search.windows.net](https://search-poc05-rag-irshad.search.windows.net))[cite: 1]. Click the copy icon[cite: 1].

In the left-hand sidebar under the Settings header, click Keys[cite: 1].

Copy the value inside the Primary admin key box[cite: 1].

3. Update Your .env File
Open .env in the root of your POC_05_FOUNDRY_RAG_AI_SEARCH_PROJECT folder and update the Azure AI Search section with your copied values[cite: 1]:

Code snippet
# ---------- Azure AI Search ----------
SEARCH_AUTH_MODE=key
AZURE_SEARCH_ENDPOINT=https://<your-search-service-name>.search.windows.net
AZURE_SEARCH_ADMIN_KEY=<your-primary-admin-key>
AZURE_SEARCH_INDEX_NAME=poc05-rag-index
(Leave AZURE_SEARCH_INDEX_NAME=poc05-rag-index unchanged; the upcoming ingestion script will auto-create this index on first run[cite: 1]).

4. Verification
From your terminal in your project directory (with your Python virtual environment activated), run the configuration check script provided in your repo[cite: 1]:

Bash
python scripts/verify_config.py
Confirm that the script outputs a successful connection status for both your Microsoft Foundry endpoints and your Azure AI Search endpoint[cite: 1].

have region not available East US 2

Having Azure AI Search in a different region from your Foundry models is completely fine. The Python code connects to each service independently over HTTPS using their respective URLs, so cross-region calls work seamlessly.  
ZIP

Follow these steps to complete the screen shown in your screenshot:

1. Fix the Resource Group
In the Resource group dropdown, change DefaultResourceGroup-CID to:

Plaintext
rg-poc05-foundry-rag
(Keeping all POC resources inside the same resource group ensures clean tracking and easy one-click deletion when you are done).

2. Choose the Best Available Location
Check the Location dropdown for (US) East US (the closest neighbor to East US 2).

If (US) East US is not available, keeping (US) Central US (currently selected) is completely fine and will not cause any errors.

3. Change Pricing Tier (Cost Warning)
Right now, your screenshot shows Standard tier, which costs around $250/month. For this beginner POC:

Click Change Pricing Tier (under Pricing tier).

Select Basic (approximately ~$70/month with Semantic Ranker support) or Free (free tier with 1 index allowed, sufficient for basic vector search).

Click Select.

4. Create the Service
Click the blue Review + create button.

Click Create.

Wait 1 to 2 minutes for provisioning to complete.

5. Once Created: Copy the Endpoint & Key
Click Go to resource.  
ZIP

On the Overview page, click the copy icon next to Url (e.g., [https://search-poc05-rag-irshad.search.windows.net](https://search-poc05-rag-irshad.search.windows.net)).  
ZIP

In the left sidebar under Settings, click Keys and copy the Primary admin key.  
ZIP

Paste both into your project's .env file:  
ZIP

Code snippet
AZURE_SEARCH_ENDPOINT=https://search-poc05-rag-irshad.search.windows.net
AZURE_SEARCH_ADMIN_KEY=PASTE_PRIMARY_ADMIN_KEY_HERE
also i need AZURE_SEARCH_INDEX_NAME=poc05-rag-index how to get also please guide me the next step

How to Handle AZURE_SEARCH_INDEX_NAME
You do not need to copy or find this name in Azure.

Your Azure AI Search service is completely empty right now. In this project architecture, you choose the name in .env, and the Python script (rag/ingest.py) will automatically create the index with that exact name inside Azure AI Search using the schema defined in rag/index_schema.py.  
ZIP

Simply keep the default value in your .env file:  
ZIP

Code snippet
AZURE_SEARCH_INDEX_NAME=poc05-rag-index
Final .env Checklist
Verify your .env file inside POC_05_FOUNDRY_RAG_AI_SEARCH_PROJECT/ has all the completed values:  
ZIP

Code snippet
# ---------- Azure AI Search ----------
SEARCH_AUTH_MODE=key
AZURE_SEARCH_ENDPOINT=https://search-poc05-rag-irshad.search.windows.net
AZURE_SEARCH_ADMIN_KEY=<PASTE_PRIMARY_ADMIN_KEY_FROM_PORTAL>
AZURE_SEARCH_INDEX_NAME=poc05-rag-index

# ---------- Microsoft Foundry / OpenAI-compatible v1 endpoint ----------
FOUNDRY_AUTH_MODE=key
FOUNDRY_OPENAI_BASE_URL=https://poc05-rag-project-eastu-resource.services.ai.azure.com/openai/v1/
FOUNDRY_API_KEY=<PASTE_FOUNDRY_KEY_FROM_PREVIOUS_STEP>
FOUNDRY_CHAT_DEPLOYMENT=Phi-4-mini-instruct
FOUNDRY_EMBEDDING_DEPLOYMENT=text-embedding-3-small

# Must exactly match the embedding length stored in Azure AI Search.
EMBEDDING_DIMENSIONS=1536
EMBEDDING_REQUEST_DIMENSIONS=false

# ---------- RAG behavior ----------
CHUNK_SIZE_TOKENS=300
CHUNK_OVERLAP_TOKENS=50
TOP_K=5
MAX_OUTPUT_TOKENS=500

# ---------- Optional observability ----------
APPLICATIONINSIGHTS_CONNECTION_STRING=

# ---------- Optional logging ----------
LOG_LEVEL=INFO
Step 9: Install Dependencies & Verify Configuration
Open your terminal, navigate into the project directory, and test connectivity:

Install requirements (if not already done):  
ZIP

Bash
pip install -r requirements.txt
Run the configuration validator:  
ZIP

Bash
python scripts/verify_config.py
Expected Output:

Validates connection to your Foundry OpenAI inference endpoint.  
ZIP

Checks that deployment Phi-4-mini-instruct responds.  
ZIP

Checks that deployment text-embedding-3-small creates vectors.  
ZIP

Validates connectivity to search-poc05-rag-irshad.search.windows.net.  
ZIP

Step 10: Ingest Documents into Azure AI Search
Once verification passes, run the ingestion pipeline:  
ZIP

Bash
python -m rag.ingest
What happens during this step:

The script reads all markdown files from data/synthetic_docs/.  
ZIP

It chunks the text according to CHUNK_SIZE_TOKENS=300 and CHUNK_OVERLAP_TOKENS=50.  
ZIP

It calls text-embedding-3-small in Foundry to generate 1536-dimensional embeddings for each chunk.  
ZIP

It creates the index named poc05-rag-index in your Azure AI Search service and uploads all document chunks with their vector embeddings.  
ZIP

Step 11: Run Smoke Test & Ask Questions
Once ingestion finishes successfully:

Run the smoke test:  
ZIP

Bash
python scripts/smoke_test.py
Query the RAG system directly:  
ZIP

Bash
python -m rag.ask --query "What is the return policy window?"
Launch the web interface (optional):  
ZIP

Bash
streamlit run rag/app.py
i try to run configuration validator getting below is fail in step 9



(common-venv-py3.12) C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\azure\poc_05_foundry_rag_ai_search_project>az group show --name rg-poc05-foundry-rag --query properties.provisioningState -o tsv

Succeeded



(common-venv-py3.12) C:\Users\ermdi\projects\ird-projects\de-ds-ai-automation\azure\poc_05_foundry_rag_ai_search_project>python scripts/verify_config.py

[OK] AZURE_SEARCH_ENDPOINT configured

[OK] Azure AI Search key authentication configured

[FAIL] FOUNDRY_OPENAI_BASE_URL must be an https endpoint containing /openai/v1

[OK] Foundry key authentication configured

[OK] Embedding dimensions: 1536

[OK] Chunking configured: size=300, overlap=50



Configuration validation FAILED with 1 issue(s).

This failure occurs because the validation script checks that FOUNDRY_OPENAI_BASE_URL begins with https:// and includes /openai/v1. When copying the endpoint from the Foundry portal, Azure only copies the host name without the API route.  
ZIP
+ 1

How to Fix
Open your .env file in the project root and update FOUNDRY_OPENAI_BASE_URL so that it includes /openai/v1/ at the end:  
ZIP

Code snippet
FOUNDRY_OPENAI_BASE_URL=https://poc05-rag-project-eastu-resource.services.ai.azure.com/openai/v1/
Note: Ensure:

There are no quotation marks around the URL ("...").

There are no spaces before or after the = sign or at the end of the line.

It includes the trailing /openai/v1/.  
ZIP

Re-run Verification
Save the .env file and run the validation command again in your terminal:  
ZIP

Bash
python scripts/verify_config.py
All items should now display [OK] and complete with

