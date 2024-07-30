# CTF_task_manager
## Description
My app

## Installation
You need docker and docker-compose

## Usage (self-hosted)
1. **Launching the container**: Launch the Docker container containing the application: `ADMIN_USER="*your_username_here*" FRESH_DB=1 docker-compose up`
    - Be sure to include quotes around username when specifying for `ADMIN_USER`
    - `FRESH_DB` takes either `1` (Drop existing database and create new one) or `0` (Keep existing DB). Option `0` is useful for when you Ctrl + C the docker container but want to relaunch it at a later date and keep all the contents.
    - You can append `--build` to the command if you make changes to eg. `Dockerfile` or any of the python files. You do not need this if you have only modified `docker-compose.yml`.
    - Do NOT launch as root/sudo. If you get permissions error, do ...
2. **Accessing the app in the browser**: The docker container exposes port 5001, and the network is a bridged connection to the host of the container.
    - That means: in order to access the Nginx server inside the container which serves the app, you can just go to `http://*your_internal_ip*:5001` or `http://127.0.0.1:5001`. Your internal ip might be DHCP-assigned address like `192.168.0.100`.
    - To allow users outside of your LAN to access the app, you need to port forward your router. I could access my router interface at `http://192.168.0.1`. The login credentials can usually either be found on the physical router or by googling the model.
      - The following port forwarding rule on the router maps the publicly available port 5002 to internal port 5001 on ip `192.168.0.101`, which is the internal ip of the host running the docker container (my Kali virtualbox). TODO: Link to img here
      - That means: When a request to `http://*my_router_ip*:5002` occurs, the router redirects it to `http://192.168.0.101:5001`, and thus the website is served to external connections.
      - You should probably also set a DHCP client reservation ip on your router, to prevent it from reassigning your ip from `192.168.0.101` to something else (because that would render the port forwarding rule useless). TODO: img here
3. **(OPTIONAL) Running the container on a virtual machine**: Set a static LAN ip on your virtual machine so the router port forwarding rule will apply.
    - When doing the port forwarding, I could only do it to ip's on the internal network (in my case `192.168.0.0/24`). My computer ip (not my Kali VM) was assigned as `192.168.0.100` by my router's DHCP server. Since I want my Kali box to host the app, I need the Kali box to have a static ip for the port forwarding rule to work. I want it to have `192.168.0.101`.
    - To achieve this, Let's change the Virtualbox standard network connection of `NAT` to `Bridged Adapter` (A bridged connection allows the host and VM to communicate with each other as if they were on the same network). I also disabled the other network adaters so only the bridged adapter was active. TODO: img here, including advanced options dropdown
    - After launching the VM with the new network confguration, I created a new Ethernet network connection TODO: img here
    - I edited this network connection with a static ("Manual" mode) ip address and provided a default gateway (this is my routers internal ip). I made sure to provide the same value as DNS server. After saving changes and disabling and enabling the connection, and making sure no other connections were active, I could access `https://google.com`. TODO: img here
    - If everything went smoothly, the host (`192.168.0.100`) should be able to ping the VM (`192.168.0.101`) and the VM should be able to access the Internet. When issuing `ip addr show` on the VM, you should see the correct inet ip. TODO: img here with red circles around ipv4 address and status UP

4. **Using the app**: You should now be able to access the app at `http://127.0.0.1:5001`. Users outside of your internal network can access it with `http://*your_router_ip*:*router_public_port*`
    - Prevent the 401 error when accessing the app by logging in as admin at `/login`. Your admin login credentials are shown in the container output in the form of a 32 char string, eg. `07b92a8a1eaa4297b2ad4f3aeda2d1ee`. After that you can add new users in `/admin`.
    - You can close the server by `Ctrl + c`:ing out of the container. You can start the server again with `FRESH_DB=0` to keep everything the way you left it.
