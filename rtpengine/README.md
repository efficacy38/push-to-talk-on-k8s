# RTPEngine
## how to bulid the image
- cd to the master `cd master`
- build the image
    - `docker build -t rtpengine .`

## how to used
- copy the config to somewhere
    - `mkdir -p /srv/docker/rtpengine`
    - `cp rtpengine.conf /srv/docker/rtpengine/`
- modify the conf `vim /srv/docker/rtpengine/rtpengine.conf`
    - interface: change to listening interface's ip
    - listen-http(ws), listen-https(wss): change to the websocket's interface ip
        - if we don't use websocket, this line can be delete
    - listen-ng: change to the ip that kamailio would access from it
        - this will run the `ng` control protocol of rtpengine
        - keep it unreachable from outside network, there has no auth about this protocol
- run the image
    - `sudo docker run -d --network host --name rtpengine -v /srv/docker/rtpengine/rtpengine.conf:/etc/rtpengine/rtpengine.conf rtpengine`

