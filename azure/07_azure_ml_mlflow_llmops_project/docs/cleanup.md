# Cleanup / cost control

## After batch endpoint validation
Run:
```bat
python azure\batch\cleanup_batch.py
```
This deletes the batch endpoint and Azure ML compute created by the deployment script.

## Optional deeper cleanup
After taking screenshots/evidence, you can delete registered model versions/data assets in Azure ML studio, then delete the entire POC resource group in Azure Portal if it contains nothing you need.

## Important cost note
Managed online endpoints can incur ongoing cost while provisioned. This project therefore uses batch deployment as the cloud-serving example and scale-to-zero AML compute. If you experiment with an online endpoint separately, delete it immediately after validation.
