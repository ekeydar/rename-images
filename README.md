# rename-images
small repo to rename images with docker

build the docker
```
docker build . -t some-image-name
```

run the docker
```
docker run -v path-to-pics-folder:/home/images some-image-name
```
