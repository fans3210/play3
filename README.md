# practice
## Installations(macos & docker desktop)

1. Make sure docker desktop & skaffold are installed.
2. Make sure your docker desktop have write access to /tmp folder since the k8s persistent volume store files in that path. You can change to what you want in these two files: mysql-pv.yaml  and celery-pv.yaml

3. Enable ingress first: 
   $ kubectl apply -f infra/others/ingress-config-macos.yaml 

4. Start the app: 
   $ skaffold dev --no-prune=false --cache-artifacts=false
   You should be able to see the webpage in localhost: 3000


## Assumptions & things to note

1. Assume that the database strucutre is same as the "order" csv file provided.
2. Assume that memory efficienty without breaking user experience is preferred compared to speed. So used batch processing of large dataframes
3. Beside some unit tests, there are files provided for test
   1. One xxx.bin file to test whether it can forbit non-csv files
   2. One empties.csv file for empty cases
   3. One mixed_empties for other empty cases such as: empty space or using NA string. However, I didn't validate for all the invalid NA strings such as "nA" or "nUlL" since I assume that these kinds of mistakes are rare
   4. 500000 sales xx.csv. File provided 
   5. orignal.csv. Smaller file which contains subset of the 500000xxx.csv data
4. Although it's required to handle large files, I still set limit to 500mb in dataservice/app/app.py since it's a bit slow for my local environment to handle larger files
5. Secret files are provided in infra/k8s/secrets.yaml and is commited together with other files to github although it's not recommmended to do so. I commited is just to simplify the installations process.
