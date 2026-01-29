# 锐捷交换机操作命令指南

---

## 零、帮助与辅助

**查询命令**：在任何模式下，输入 `?` 可查询当前可用的命令或参数帮助。
**补全命令**：输入命令前缀后按 `Tab` 键或输入 `?` 可自动补全。
**进入配置模式**：输入 `configure terminal` 或 `conf t` 进入全局配置模式。
**返回上一级**：输入 `exit` 返回上一级模式。

**默认连接信息**：
- 串口波特率：9600
- 默认用户：admin
- 默认密码：admin

---

## 一、VLAN配置命令

### 基本VLAN配置

Ruijie> enable
Ruijie# configure terminal
Ruijie(config)# vlan <vlan_id>
Ruijie(config-vlan)# name <vlan_name>
Ruijie(config-vlan)# exit
Ruijie(config)# interface <interface-id>
Ruijie(config-if)# switchport mode {access | trunk | hybrid}
Ruijie(config-if)# switchport access vlan <vlan_id>
Ruijie(config-if)# switchport trunk allowed vlan <vlan_list>
Ruijie(config-if)# switchport trunk native vlan <vlan_id>
Ruijie(config-if)# switchport hybrid allowed vlan <vlan_list> tagged
Ruijie(config-if)# switchport hybrid allowed vlan <vlan_list> untagged

### VLAN维护

Ruijie# show vlan
Ruijie# show vlan <vlan_id>
Ruijie# show vlan brief
Ruijie# show interfaces switchport

---

## 二、链路聚合命令（Port-channel）

### 创建聚合接口

Ruijie# configure terminal
Ruijie(config)# interface Port-channel 10
Ruijie(config-if)# switchport mode trunk
Ruijie(config-if)# switchport trunk allowed vlan all
Ruijie(config-if)# exit

### 将物理接口加入聚合组

Ruijie(config)# interface GigabitEthernet 0/1
Ruijie(config-if)# channel-group 10 mode on
Ruijie(config-if)# exit

Ruijie(config)# interface GigabitEthernet 0/2
Ruijie(config-if)# channel-group 10 mode on
Ruijie(config-if)# exit

### 配置LACP模式

Ruijie(config)# interface Port-channel 10
Ruijie(config-if)# port-channel load-balance src-dst-ip
Ruijie(config-if)# exit

Ruijie(config)# interface GigabitEthernet 0/1
Ruijie(config-if)# channel-group 10 mode active
Ruijie(config-if)# exit

Ruijie(config)# interface GigabitEthernet 0/2
Ruijie(config-if)# channel-group 10 mode passive
Ruijie(config-if)# exit

### 聚合维护命令

Ruijie# show etherchannel summary
Ruijie# show etherchannel detail
Ruijie# show etherchannel load-balance
Ruijie# show interfaces port-channel 10

---

## 三、路由配置命令

### 静态路由

Ruijie(config)# ip route <dest-address> <mask> <next-hop-address> [distance]
Ruijie(config)# ip route 0.0.0.0 0.0.0.0 <next-hop-address>

**配置示例**：

Ruijie(config)# ip route 192.168.100.0 255.255.255.0 192.168.1.1
Ruijie(config)# ip route 0.0.0.0 0.0.0.0 192.168.1.254

### VLAN接口IP配置

Ruijie(config)# interface vlan 100
Ruijie(config-if)# ip address 192.168.100.1 255.255.255.0
Ruijie(config-if)# no shutdown
Ruijie(config-if)# exit

### 路由维护

Ruijie# show ip route
Ruijie# show ip route verbose
Ruijie# show ip interface brief

---

## 四、系统与基础接口配置

### 系统管理

Ruijie> enable
Ruijie# configure terminal
Ruijie(config)# hostname <hostname>
Ruijie(config)# line console 0
Ruijie(config-line)# login
Ruijie(config-line)# password <password>
Ruijie(config)# line vty 0 4
Ruijie(config-line)# login local
Ruijie(config)# username admin password Admin@123 privilege 15
Ruijie(config)# write
Ruijie# show running-config
Ruijie# show startup-config

### 接口管理

Ruijie(config)# interface <interface-id>
Ruijie(config-if)# description <description-text>
Ruijie(config-if)# no shutdown
Ruijie(config-if)# shutdown
Ruijie(config-if)# speed {10 | 100 | 1000 | auto}
Ruijie(config-if)# duplex {full | half | auto}
Ruijie(config-if)# ip address <ip-address> <mask>
Ruijie(config-if)# no ip address

### DHCP服务

Ruijie(config)# service dhcp
Ruijie(config)# ip dhcp pool VLAN100
Ruijie(config-dhcp)# network 192.168.100.0 255.255.255.0
Ruijie(config-dhcp)# default-router 192.168.100.1
Ruijie(config-dhcp)# dns-server 8.8.8.8 114.114.114.114
Ruijie(config-dhcp)# lease 7

---

## 五、通用维护命令

Ruijie# show version
Ruijie# show running-config
Ruijie# show startup-config
Ruijie# show interfaces brief
Ruijie# show interfaces <interface-name>
Ruijie# show cpu
Ruijie# show memory
Ruijie# show logging
Ruijie# show arp
Ruijie# show mac-address-table
Ruijie# show flash

---

## 六、系统操作

Ruijie# erase startup-config
Ruijie# reload
Ruijie# write
Ruijie# dir
Ruijie# delete flash:<filename>

---

## 七、调试命令

Ruijie# ping <ip-address>
Ruijie# traceroute <ip-address>
Ruijie# show ip interface brief
Ruijie# show ip route
