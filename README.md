# CTF_task_manager
## Description
I got tired of having to constantly ping my friend to check if he had already started on a CTF challenge I wanted to do. So I made this:
![](https://github.com/Jonnen98cool/CTF_task_manager/blob/main/readme_helper/app_snapshot.png)

## Installation
You need docker-compose.

**Linux**:  
`sudo apt install docker-compose`  
(make sure you also add your user to the `docker` group if you haven't already, see section **Troubleshooting**)

**Windows**:  
Not tested, you are on your own. Using Linux in a VM is recommended.

## Usage (self-hosted)
### TLDR version
1. Launch container: `ADMIN_USER="*your_username_here*" FRESH_DB=1 docker-compose up`
2. Determine your PC's ip address (probably DHCP-assigned), port forward to internal port 5001 on your router: ![](https://github.com/Jonnen98cool/CTF_task_manager/blob/main/readme_helper/router_port_forwarding_rule.png)
3. **(Optional, if running in VM)** Port forward VM: ![](https://github.com/Jonnen98cool/CTF_task_manager/blob/main/readme_helper/virtualbox_port_forwarding_rule.png)
4. You are done, access app at `http://127.0.0.1:5001`, Tell your friends to access it at `http://*router_ip*:5002`

### Long version
1. **Launching the container**: Launch the Docker container containing the application: `ADMIN_USER="*your_username_here*" FRESH_DB=1 docker-compose up`
    - Be sure to include quotes around username when specifying for `ADMIN_USER`
    - `FRESH_DB` takes either `1` (Drop existing database and create new one) or `0` (Keep existing DB). Option `0` is useful for when you Ctrl + C the docker container but want to relaunch it at a later date and keep all the contents.
    - You can append `--build` to the command if you make changes to eg. `Dockerfile` or any of the python files. You do not need this if you have only modified `docker-compose.yml`.
    - For security reasons, it is NOT recommended to launch as root/sudo. It should not be necessary. See section **Troubleshooting** if you are having issues.

2. **Accessing the app in the browser**: The docker container exposes the server on port 5001 and the same ip as its host. You need to port forward your router.
    - In order to access the Nginx server running inside the container, you can just go to `http://*your_internal_ip*:5001` or `http://127.0.0.1:5001`. Your internal ip might be a DHCP-assigned address like `192.168.0.100`.
    - To allow users outside of your LAN to access the app, you need to port forward your router. I could access my router interface at `http://192.168.0.1`. The login credentials can usually either be found on the physical router or by googling the model.
      - The following port forwarding rule on the router maps the publicly available port 5002 to internal port 5001 on ip `192.168.0.100`, which is the ip of my PC. ![](https://github.com/Jonnen98cool/CTF_task_manager/blob/main/readme_helper/router_port_forwarding_rule.png)
      - That means: When a request to `http://*my_router_ip_redacted*:5002` occurs, the router redirects it to the service running on `192.168.0.100` at port `5001`.
      - While possibly not necessary, you could also set a DHCP client reservation ip on your router, to prevent it from reassigning your ip from `192.168.0.100` to something else (because that would render the port forwarding rule useless). ![](https://github.com/Jonnen98cool/CTF_task_manager/blob/main/readme_helper/router_dhcp_reservation.png)

3. **(OPTIONAL) Running the container on a virtual machine**: You need to port forward the VM in Virtualbox settings. It's OK to do this while the VM is running.
    - The standard network settings for Virtualbox is `NAT`. Leave it at that, and select the `Advanced` dropdown and click on `Port Forwarding`. ![](https://github.com/Jonnen98cool/CTF_task_manager/blob/main/readme_helper/virtualbox_port_forwarding.png)
    - Configure port forwarding such that the host ip forwards to the VM/Guest NAT ip (by default `10.0.2.15`) on port 5001 which the container server is running at. ![](https://github.com/Jonnen98cool/CTF_task_manager/blob/main/readme_helper/virtualbox_port_forwarding_rule.png)
    - What you have configured so far:  
    Request from Internet to your router `http://*redacted*:5002` --> router port forwarding rule forwards request to service running at `192.168.0.100:5001` --> Virtualbox port forwarding rule engages, request forwarded to VM service running at `10.0.2.15:5001` --> VM docker container has port 5001 exposed and the network is bridged, so request gets sent to container Nginx server listening on 5001.

4. **Using the app**: You should now be able to access the app at `http://127.0.0.1:5001`. Users outside of your internal network can access it with `http://*your_router_ip*:*router_public_port*` (find your router's external ip: [https://www.whatsmyip.org/](https://www.whatsmyip.org/) ). Note that you will not be able to access the app at your routers external ip from within its internal network, you have to go through localhost. 
    - Prevent the 401 redirect when accessing the app by logging in at `/login`. Your admin login credentials are shown in the container output in the form of a 32 char string, eg. `07b92a8a1eaa4297b2ad4f3aeda2d1ee`. After that you can add new users in `/admin`.
    - You can close the server by `Ctrl + c`:ing out of the container. You can start the server again with `FRESH_DB=0` to keep everything the way you left it.
  
### Troubleshooting
- When trying to launch `docker-compose`, if you get: `ERROR: Couldn't connect to Docker daemon at http+docker://localunixsocket - is it running?` make sure you have added your user to the docker group:
    - Add your user to `docker` group: `sudo usermod -aG docker $USER` (input this command literally, don't change `$USER`) 
    - Refresh session: `newgrp docker` 
