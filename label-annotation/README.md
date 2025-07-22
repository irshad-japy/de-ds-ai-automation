give full permision for first time of data:
chmod -R 777 /home/ec2-user/my_pyautomation/scripts/ds/label-annotation/ls-data

docker run : 
docker run -it -p 8080:8080 -v /home/ec2-user/my_pyautomation/scripts/ds/label-annotation/ls-data:/lab
el-studio/data heartexlabs/label-studio:latest

label-studio docs:
https://labelstud.io/guide/glossary
https://labelstud.io/learn/getting-started-with-label-studio/setting-up-label-studio/
https://labelstud.io/guide/quick_start


chatgpt refrence:
https://chatgpt.com/c/674aa829-f1b4-800d-989d-f7779c40b9a0