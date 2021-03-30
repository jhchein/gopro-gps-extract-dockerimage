az acr login --name bikevideoregistry && ^
docker image build --build-arg tenant_id=%goprotenant_id% --build-arg client_id=%goproclient_id% --build-arg client_secret=%goproclient_secret% -t bikevideoregistry.azurecr.io/goproextraction . && ^
docker push bikevideoregistry.azurecr.io/goproextraction