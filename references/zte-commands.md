# 中兴交换机操作命令指南

---

## 零、帮助与辅助

**查询命令**：在任何模式下，输入 `?` 可查询当前可用的命令或参数帮助。
**补全命令**：输入命令前缀后按 `Tab` 键可自动补全。
**进入配置模式**：输入 `enable` 进入全局配置模式。

**默认连接信息**：
- 串口波特率：115200
- 默认密码：MSR_adm10、zxr10、ZXWT

---

## 一、VLAN配置命令

### 基本VLAN配置

ZXWT> enable
ZXWT# configure terminal
ZXWT(config)# switchvlan-configuration
ZXWT(config-swvlan)# vlan <vlan_id>
ZXWT(config-swvlan-vlan)# name <vlan_name>
ZXWT(config-swvlan-vlan)# exit
ZXWT(config-swvlan)# interface <interface-name>
ZXWT(config-swvlan-if-<interface-name>)# switchport mode {access | hybrid | trunk}
ZXWT(config-swvlan-if-<interface-name>)# switchport access vlan <vlan_id>
ZXWT(config-swvlan-if-<interface-name>)# switchport trunk native vlan <vlan_id>
ZXWT(config-swvlan-if-<interface-name>)# switchport hybrid native vlan <vlan_id>
ZXWT(config-swvlan-if-<interface-name>)# switchport trunk vlan <vlan_list>
ZXWT(config-swvlan-if-<interface-name>)# switchport hybrid vlan <vlan_list> {tag | untag}

### VLAN维护

ZXWT# show vlan
ZXWT# show running-config switchvlan

---

## 二、链路聚合命令（LACP）

### LACP动态聚合配置流程

**步骤1：创建聚合口并切换二层属性**

ZXWT(config)# interface smartgroup10
ZXWT(config-if-smartgroup10)# switch attribute enable
ZXWT(config-if-smartgroup10)# exit

**步骤2：配置物理接口加入聚合组**

ZXWT(config)# interface gei-4/3
ZXWT(config-if-gei-4/3)# switch attribute enable
ZXWT(config-if-gei-4/3)# exit

ZXWT(config)# interface gei-4/4
ZXWT(config-if-gei-4/4)# switch attribute enable
ZXWT(config-if-gei-4/4)# exit

**步骤3：配置LACP协议**

ZXWT(config)# lacp
ZXWT(config-lacp)# interface smartgroup10
ZXWT(config-lacp-sg-if-smartgroup10)# lacp mode 802.3ad
ZXWT(config-lacp-sg-if-smartgroup10)# exit

ZXWT(config-lacp)# interface gei-4/3
ZXWT(config-lacp-member-if-gei-4/3)# smartgroup 10 mode active
ZXWT(config-lacp-member-if-gei-4/3)# exit

ZXWT(config-lacp)# interface gei-4/4
ZXWT(config-lacp-member-if-gei-4/4)# smartgroup 10 mode active
ZXWT(config-lacp-member-if-gei-4/4)# exit
ZXWT(config-lacp)# exit

**步骤4：配置Trunk VLAN（如需要）**

ZXWT(config)# switchvlan-configuration
ZXWT(config-swvlan)# interface smartgroup10
ZXWT(config-swvlan-if-smartgroup10)# switchport mode trunk
ZXWT(config-swvlan-if-smartgroup10)# switchport trunk vlan 20
ZXWT(config-swvlan-if-smartgroup10)# exit
ZXWT(config-swvlan)# exit

### 聚合维护命令

ZXWT# show lacp <group-number> internal
ZXWT# show lacp internal

---

## 三、路由配置命令

### 静态路由

ZXWT(config)# ip route <prefix> <net-mask> <forwarding-router's-address>
ZXWT(config)# ip route 0.0.0.0 0.0.0.0 <next-hop-ip>
ZXWT(config)# ip route <prefix> <net-mask> <next-hop-ip> <priority>

**配置示例**：

ZXWT(config)# ip route 1.1.1.1/32 192.168.20.1

### VLAN接口IP配置

ZXWT(config)# interface vlan20
ZXWT(config-if-vlan20)# ip address 192.168.20.2/24
ZXWT(config-if-vlan20)# exit

### 路由维护

ZXWT# show ip forwarding route
ZXWT# show ip interface brief

---

## 四、L2TP配置命令（LNS端完整配置）

### 完整配置流程示例

**步骤1：配置物理接口**

ZXWT(config)# interface gei-4/8
ZXWT(config-if-gei-4/8)# no shutdown
ZXWT(config-if-gei-4/8)# ip address 77.77.77.1/24
ZXWT(config-if-gei-4/8)# exit

**步骤2：配置Loopback接口（用于VPN地址）**

ZXWT(config)# interface loopback20
ZXWT(config-if-loopback20)# ip address 192.168.11.254/32
ZXWT(config-if-loopback20)# exit

**步骤3：配置IP地址池**

ZXWT(config)# ip pool zte
ZXWT(config-ip-pool)# range 192.168.11.1 192.168.11.250 255.255.255.0
ZXWT(config-ip-pool)# exit

**步骤4：配置虚拟模板接口**

ZXWT(config)# interface virtual_template10
ZXWT(config-if-virtual_template10)# mode ppp
ZXWT(config-if-virtual_template10)# ip unnumbered loopback20
ZXWT(config-if-virtual_template10)# exit

**步骤5：配置PPP认证**

ZXWT(config)# ppp
ZXWT(config-ppp)# interface virtual_template10
ZXWT(config-ppp-if-virtual_template10)# bind-ip-pool zte
ZXWT(config-ppp-if-virtual_template10)# ppp authentication chap
ZXWT(config-ppp-if-virtual_template10)# exit
ZXWT(config-ppp)# exit

**步骤6：配置VPDN组**

ZXWT(config)# vpdn-group zte
ZXWT(config-vpdn-group)# service-type lns
ZXWT(config-vpdn-group)# virtual-template 10
ZXWT(config-vpdn-group)# exit

**步骤7：启用VPDN并设置默认组**

ZXWT(config)# vpdn
ZXWT(config-vpdn)# enable
ZXWT(config-vpdn)# default vpdn-group zte
ZXWT(config-vpdn)# exit

**步骤8：配置用户认证**

ZXWT(config)# subscriber-manage
ZXWT(config-submanage)# authentication-template zte
ZXWT(config-submanage-authen-template)# authentication-type local
ZXWT(config-submanage-authen-template)# exit

ZXWT(config-submanage)# domain l2tp
ZXWT(config-submanage-domain)# bind authentication-template zte
ZXWT(config-submanage-domain)# tunnel-domain enable
ZXWT(config-submanage-domain)# exit

ZXWT(config-submanage)# local-subscriber lac1 domain-name l2tp password 123
ZXWT(config-submanage-local-sub)# exit
ZXWT(config-submanage)# exit

### L2TP维护命令

ZXWT# show subscriber all
ZXWT# show vpdn

---

## 五、系统与基础接口配置

### 系统管理

ZXWT(config)# hostname <name>
ZXWT(config)# username <user> password <password>
ZXWT(config)# enable secret <password>
ZXWT# write
ZXWT# reload

### 接口管理

ZXWT(config)# interface <interface-name>
ZXWT(config-if-<interface-name>)# ip address <ip> <mask>
ZXWT(config-if-<interface-name>)# no shutdown
ZXWT(config-if-<interface-name>)# description <text>
ZXWT(config-if-<interface-name>)# speed {10 | 100 | 1000 | auto}
ZXWT(config-if-<interface-name>)# duplex {full | half | auto}

### DHCP服务

ZXWT(config)# ip dhcp server enable
ZXWT(config)# ip pool <pool-name>
ZXWT(config-ip-pool)# network <ip> <mask>
ZXWT(config-ip-pool)# default-router <gateway>
ZXWT(config-ip-pool)# dns-server <dns>

---

## 六、通用维护命令

ZXWT# show running-config
ZXWT# show interface <interface-name>
ZXWT# show vlan
ZXWT# show lacp <group-number> internal
ZXWT# show ip forwarding route
ZXWT# show ip interface brief
ZXWT# show version
ZXWT# show processor
ZXWT# show memory
ZXWT# show logging

---

## 七、端口模式切换

ZXWT(config-if-<interface-name>)# switch attribute enable
ZXWT(config-if-<interface-name>)# port attribute layer3
ZXWT(config-if-<interface-name>)# port attribute layer2
