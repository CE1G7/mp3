# mp3

## Task 1.3
Execute into either camera container and run:       
```curl -sv -m 3 http://10.10.1.10:8080```
Inside the same container run:
```curl -sv -m 3 http://10.20.0.30:8080```

Observe the logs.

## Task 1.5
Execute into either fog container and ping the cloud container. Observe the logs.

## Task 2
run ```dockerc compose up``` and observe the logs

To run dos attack add --dos flag to one of the cams in the compose file.