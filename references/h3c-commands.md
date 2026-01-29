# 华三（H3C）交换机操作命令指南

---

## 零、帮助与辅助

**查询命令**：在任何模式下，输入 `?` 可查询当前可用的命令或参数帮助。
**补全命令**：输入命令前缀后按 `Tab` 键或输入 `?` 可自动补全。
**进入配置模式**：输入 `system-view` 进入系统视图。
**返回上一级**：输入 `quit` 或 `q` 返回上一级模式。

**默认连接信息**：
- 串口波特率：9600
- 默认用户：admin
- 默认密码：admin

---

## 一、VLAN配置命令

### 基本VLAN配置

<H3C> system-view
[H3C] vlan <vlan_id>
[H3C-vlan<vlan_id>]# name <vlan_name>
[H3C-vlan<vlan_id>]# description <description>
[H3C-vlan<vlan_id>]# quit
[H3C] interface <interface-type> <interface-number>
[H3C-<interface-name>]# port link-type {access | trunk | hybrid}
[H3C-<interface-name>]# port access vlan <vlan_id>
[H3C-<interface-name>]# port trunk permit vlan <vlan_list>
[H3C-<interface-name>]# port hybrid pvid vlan <vlan_id>
[H3C-<interface-name>]# port hybrid vlan <vlan_list> tagged
[H3C-<interface-name>]# port hybrid vlan <vlan_list> untagged

### VLAN维护

[H3C] display vlan
[H3C] display vlan <vlan_id>
[H3C] display port vlan

---

## 二、链路聚合命令（Link-aggregation）

### 创建聚合接口

<H3C> system-view
[H3C] interface Bridge-Aggregation 10
[H3C-Bridge-Aggregation10]# port link-type trunk
[H3C-Bridge-Aggregation10]# port trunk permit vlan all
[H3C-Bridge-Aggregation10]# quit

### 将物理接口加入聚合组

[H3C] interface GigabitEthernet1/0/1
[H3C-GigabitEthernet1/0/1]# port link-aggregation group 10
[H3C-GigabitEthernet1/0/1]# quit

[H3C] interface GigabitEthernet1/0/2
[H3C-GigabitEthernet1/0/2]# port link-aggregation group 10
[H3C-GigabitEthernet1/0/2]# quit

### 配置LACP模式

<H3C] interface Bridge-Aggregation 10
[H3C-Bridge-Aggregation10]# link-aggregation mode dynamic
[H3C-Bridge-Aggregation10]# quit

### 聚合维护命令

[H3C] display link-aggregation summary
[H3C] display link-aggregation verbose
[H3C] display link-aggregation member-port
[H3C] display link-aggregation interface Bridge-Aggregation 10

---

## 三、路由配置命令

### 静态路由

[H3C] ip route-static <dest-address> <mask> <next-hop-address> [preference <value>]
[H3C] ip route-static 0.0.0.0 0.0.0.0 <next-hop-address>

**配置示例**：

[H3C] ip route-static 192.168.100.0 255.255.255.0 192.168.1.1
[H3C] ip route-static 0.0.0.0 0.0.0.0 192.168.1.254

### VLAN接口IP配置

[H3C] interface Vlan-interface 100
[H3C-Vlan-interface100]# ip address 192.168.100.1 255.255.255.0
[H3C-Vlan-interface100]# quit

### 路由维护

[H3C] display ip routing-table
[H3C] display ip routing-table verbose
[H3C] display ip interface brief

---

## 四、系统与基础接口配置

### 系统管理

<H3C> system-view
[H3C] sysname <hostname>
[H3C] user-interface aux 0
[H3C] user-interface vty 0 4
[H3C-line-vty0-4]# authentication-mode scheme
[H3C-line-vty0-4]# set authentication password simple <password>
[H3C] local-user <username>
[H3C-luser-<username>]# password simple <password>
[H3C-luser-<username>]# service-type telnet
[H3C-luser-<username>]# authorization-attribute level 3
[H3C-luser-<username>]# quit
[H3C] save
[H3C] display current-configuration
[H3C] display saved-configuration

### 接口管理

[H3C] interface <interface-type> <interface-number>
[H3C-<interface-name>]# description <description-text>
[H3C-<interface-name>]# undo shutdown
[H3C-<interface-name>]# speed {10 | 100 | 1000 | auto}
[H3C-<interface-name>]# duplex {full | half | auto}
[H3C-<interface-name>]# ip address <ip-address> <mask>
[H3C-<interface-name>]# undo ip address

### DHCP服务

[H3C] dhcp enable
[H3C] dhcp server ip-pool VLAN100
[H3C-dhcp-pool-VLAN100]# network 192.168.100.0 mask 255.255.255.0
[H3C-dhcp-pool-VLAN100]# gateway-list 192.168.100.1
[H3C-dhcp-pool-VLAN100]# dns-list 8.8.8.8 114.114.114.114
[H3C-dhcp-pool-VLAN100]# lease day 7

---

## 五、通用维护命令

<H3C> display version
<H3C> display device
<H3C> display interface brief
<H3C> display interface <interface-name>
<H3C> display cpu
<H3C> display memory
<H3C> display logbuffer
<H3C> display arp
<H3C> display mac-address
<H3C] display current-configuration | include <keyword>

---

## 六、系统操作

<H3C> reset saved-configuration
<H3C> reboot
<H3C> clock datetime <HH:MM:SS> <YYYY-MM-DD>
<H3C> display clock

---

## 七、调试命令

<H3C> ping <ip-address>
<H3C> tracert <ip-address>
<H3C] display ip interface brief
[H3C] display ip routing-table
