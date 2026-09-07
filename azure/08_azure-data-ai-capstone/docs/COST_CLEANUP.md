# Cost cleanup

At the end of the lab:

1. Terminate Databricks compute.
2. Stop/delete Azure ML compute or online endpoints used by POC-07 if no longer needed.
3. Delete temporary Foundry model deployments if they incur cost and are not reused.
4. Delete Event Hubs if the lab is complete.
5. Delete paid Azure AI Search if it was created only for this POC.
6. Remove temporary SQL/Synapse/Fabric resources that are not part of another POC.
7. If everything was created in the dedicated Terraform resource group, run `terraform destroy` or delete the resource group after verifying no shared resources are inside it.
8. Open Cost Management and verify that no unexpected lab resources remain.
