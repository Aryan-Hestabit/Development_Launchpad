# Linux inside Docker Container
## Entering Container

Building Docker Imgae:
```bash
docker build -t node-app
```
![Imgaes](./Screenshots/DockerImages.png)


Running Container:
```bash
docker run -d -p 3000:3000 --name node-container node-app
```

![Docker Container in Browser](./Screenshots/Container.png)

Command:
```bash
docker exec -it node-container /bin/sh
```

## Linux command Outputs:

![result1](./Screenshots/Result1.png)
![ps](./Screenshots/ps.png)
![top](./Screenshots/top.png)
![Disk Uage](./Screenshots/DiskUsage.png)


## Docker Logs

![Docker Logs](./Screenshots/DockerLogs.png)

### verification
![Browser](./Screenshots/Browser.png)