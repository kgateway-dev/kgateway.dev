1. Create the namespaces for `team1` and `team2`. 
   ```sh
   kubectl create namespace team1
   kubectl create namespace team2
   ```

2. Deploy the httpbin app into both namespaces. 
   ```sh
   kubectl -n team1 apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
   kubectl -n team2 apply -f https://raw.githubusercontent.com/kgateway-dev/kgateway.dev/main/assets/docs/examples/httpbin.yaml
   ```

3. Verify that the httpbin apps are up and running. 
   ```sh
   kubectl get pods -n team1
   kubectl get pods -n team2
   ```
   
   Example output: 
   ```
   NAME                      READY   STATUS    RESTARTS   AGE
   httpbin-f46cc8b9b-bzl9z   3/3     Running   0          7s
   NAME                      READY   STATUS    RESTARTS   AGE
   httpbin-f46cc8b9b-nhtmg   3/3     Running   0          6s
   ```