# 思科（Cisco）交换机操作命令指南

---

## 零、帮助与辅助

**查询命令**：在任何模式下，输入 `?` 可查询当前可用的命令或参数帮助。
**补全命令**：输入命令前缀后按 `Tab` 键或输入 `?` 可自动补全。
**进入配置模式**：输入 `configure terminal` 或 `conf t` 进入全局配置模式。
**返回上一级**：输入 `exit` 返回上一级模式。

**默认连接信息**：
- 串口波特率：9600
- 默认用户：cisco
- 默认密码：cisco 或 enable密码

---

## 一、VLAN配置命令

### 基本VLAN配置

Switch> enable
Switch# configure terminal
Switch(config)# vlan <vlan_id>
Switch(config-vlan)# name <vlan_name>
Switch(config-vlan)# exit
Switch(config)# interface <interface-id>
Switch(config-if)# switchport mode {access | trunk | dynamic}
Switch(config-if)# switchport access vlan <vlan_id>
Switch(config-if)# switchport trunk allowed vlan <vlan_list>
Switch(config-if)# switchport trunk native vlan <vlan_id>

### VLAN维护

Switch# show vlan
Switch# show vlan <vlan_id>
Switch# show vlan brief
Switch# show interfaces switchport

---

## 二、链路聚合命令（EtherChannel）

### 创建聚合接口

Switch# configure terminal
Switch(config)# interface Port-channel 10
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan all
Switch(config-if)# exit

### 将物理接口加入聚合组

Switch(config)# interface range GigabitEthernet 0/1 - 2
Switch(config-if-range)# channel-group 10 mode on
Switch(config-if-range)# exit

### 配置LACP模式

Switch(config)# interface range GigabitEthernet 0/1 - 2
Switch(config-if-range)# channel-group 10 mode active
Switch(config-if-range)# exit

Switch(config)# interface Port-channel 10
Switch(config-if)# port-channel load-balance src-dst-ip
Switch(config-if)# exit

### 聚合维护命令

Switch# show etherchannel summary
Switch# show etherchannel detail
Switch# show etherchannel load-balance
Switch# show interfaces port-channel 10

---

## 三、路由配置命令

### 静态路由

Switch(config)# ip route <dest-address> <mask> <next-hop-address> [administrative-distance]
Switch(config)# ip route 0.0.0.0 0.0.0.0 <next-hop-address>

**配置示例**：

Switch(config)# ip route 192.168.100.0 255.255.255.0 192.168.1.1
Switch(config)# ip route 0.0.0.0 0.0.0.0 192.168.1.254

### VLAN接口IP配置

Switch(config)# interface vlan 100
Switch(config-if)# ip address 192.168.100.1 255.255.255.0
Switch(config-if)# no shutdown
Switch(config-if)# exit

### 路由维护

Switch# show ip route
Switch# show ip route verbose
Switch# show ip interface brief

---

## 四、系统与基础接口配置

### 系统管理

Switch> enable
Switch# configure terminal
Switch(config)# hostname <hostname>
Switch(config)# username <username> privilege <level> secret <password>
Switch(config)# enable secret <password>
Switch(config)# enable password <password>
Switch(config)# line console 0
Switch(config-line)# login local
Switch(config)# line vty 0 4
Switch(config-line)# login local
Switch(config-line)# transport input {ssh | telnet}
Switch# write memory
Switch# copy running-config startup-config
Switch# show running-config
Switch# show startup-config

### 接口管理

Switch(config)# interface <interface-id>
Switch(config-if)# description <description-text>
Switch(config-if)# no shutdown
Switch(config-if)# shutdown
Switch(config-if)# speed {10 | 100 | 1000 | auto}
Switch(config-if)# duplex {full | half | auto}
Switch(config-if)# ip address <ip-address> <mask>
Switch(config-if)# no ip address

### DHCP服务配置

Switch(config)# service dhcp
Switch(config)# ip dhcp excluded-address 192.168.100.1 192.168.100.10
Switch(config)# ip dhcp pool VLAN100
Switch(dhcp-config)# network 192.168.100.0 255.255.255.0
Switch(dhcp-config)# default-router 192.168.100.1
Switch(dhcp-config)# dns-server 8.8.8.8 114.114.114.114
Switch(dhcp-config)# lease 7

---

## 五、通用维护命令

Switch# show version
Switch# show running-config
Switch# show startup-config
Switch# show interfaces brief
Switch# show interfaces <interface-name>
Switch# show processes cpu
Switch# show memory
Switch# show logging
Switch# show arp
Switch# show mac address-table
Switch# show flash
Switch# show inventory
Switch# show environment

---

## 六、系统操作

Switch# erase startup-config
Switch# reload
Switch# write memory
Switch# dir flash:
Switch# delete flash:<filename>

---

## 七、调试命令

Switch# ping <ip-address>
Switch# traceroute <ip-address>
Switch# show ip interface brief
Switch# show ip route
