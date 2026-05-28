# classic-models-api

## Create new project

```sh
export DEPLOY_NAMESPACE=demoapp-classic-models
oc new-project $DEPLOY_NAMESPACE
```

## Install MySQL DB

Using built-in Openshift MySQL template (mysql-persistent):

```sh
export MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32)
export MYSQL_SERVICE_NAME="classicmodelsdb"
export MYSQL_APP_DB="classicmodels"
export MYSQL_APP_USER="classicuser"
export MYSQL_APP_PASSWORD=$(openssl rand -base64 32)

oc new-app mysql-persistent \
    -n ${DEPLOY_NAMESPACE} \
    -p DATABASE_SERVICE_NAME=${MYSQL_SERVICE_NAME} \
    -p MYSQL_USER=${MYSQL_APP_USER} \
    -p MYSQL_PASSWORD=${MYSQL_APP_PASSWORD} \
    -p MYSQL_DATABASE=${MYSQL_APP_DB} \
    -p MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
    -p INIT_CONFIGMAP_NAME="classic-models-dbinit" \
    -p VOLUME_CAPACITY=1Gi
```

Then, simple manual script run to initialize (one time only)

NOTE: WAIT for DB to be ready!

```sh
mpod=$(oc get pods --selector name=classicmodelsdb --output name | awk -F/ '{print $NF}')
oc cp ../db/mysqlsampledatabase.sql ${mpod}:/tmp/mysqlsampledatabase.sql
oc exec ${mpod} -- bash -c "mysql --user=root < /tmp/mysqlsampledatabase.sql"
oc exec ${mpod} -- bash -c "mysql --user=root -e 'use classicmodels; SELECT * FROM productlines;'"
```

## Install App with production values

```sh
export DJANGO_SECRET=$(openssl rand -base64 50 | tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' | head -c 50)
export APIKEY_SECRET=$(openssl rand -base64 50 | tr -dc 'a-zA-Z0-9!@#$%^&*(-_=+)' | head -c 50)
helm install classic-models-api ../helm/classic-models-api \
  -n ${DEPLOY_NAMESPACE} \
  --values ./helm-production.yaml \
  --set app.secretKey="$DJANGO_SECRET" \
  --set app.apiKey="$APIKEY_SECRET" \
  --set app.allowedHosts="*" \
  --set mysql.enabled=false \
  --set mysql.externalHost=${MYSQL_SERVICE_NAME} \
  --set mysql.externalPort=3306 \
  --set mysql.auth.database=${MYSQL_APP_DB} \
  --set mysql.auth.username=${MYSQL_APP_USER} \
  --set mysql.auth.password=${MYSQL_APP_PASSWORD}
```

URL for the Docs: https://classic-models-api-demoapp-classic-models.<YOURDOMAIN>/classic-models/api/docs/

## Passwords / Secrets

Save all the secrets created in a safe place:

```sh
echo "MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD"
echo "MYSQL_SERVICE_NAME=$MYSQL_SERVICE_NAME"
echo "MYSQL_APP_DB=$MYSQL_APP_DB"
echo "MYSQL_APP_USER=$MYSQL_APP_USER"
echo "MYSQL_APP_PASSWORD=$MYSQL_APP_PASSWORD"
echo "DJANGO_SECRET=$DJANGO_SECRET"
echo "APIKEY_SECRET=$APIKEY_SECRET"
```

## Uninstall

Delete the app first

```sh
helm delete classic-models-api -n ${DEPLOY_NAMESPACE}
```

Delete the DB second

```sh
oc delete dc ${MYSQL_SERVICE_NAME} -n ${DEPLOY_NAMESPACE}
oc delete svc ${MYSQL_SERVICE_NAME} -n ${DEPLOY_NAMESPACE}
oc delete pvc ${MYSQL_SERVICE_NAME} -n ${DEPLOY_NAMESPACE}
oc delete secret ${MYSQL_SERVICE_NAME} -n ${DEPLOY_NAMESPACE}
```
