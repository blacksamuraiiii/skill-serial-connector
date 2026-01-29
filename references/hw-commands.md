# 华为交换机操作命令指南

---

## 零、帮助与辅助

**查询命令**：在任何模式下，输入 `?` 可查询当前可用的命令或参数帮助。
**补全命令**：输入命令前缀后按 `Tab` 键或输入 `?` 可自动补全。
**进入配置模式**：输入 `system-view` 进入系统视图。
**返回上一级**：输入 `quit` 或 `q` 返回上一级模式。

**默认连接信息**：
- 串口波特率：9600 或 115200
- 默认用户：admin
- 默认密码：admin@123 或空

---

## 一、VLAN配置命令

### 基本VLAN配置

<Huawei> system-view
[Huawei] vlan <vlan_id>
[Huawei-vlan<vlan_id>]# name <vlan_name>
[Huawei-vlan<vlan_id>]# quit
[Huawei] interface <interface-type> <interface-number>
[Huawei-<interface-name>]# port link-type {access | trunk | hybrid}
[Huawei-<interface-name>]# port default vlan <vlan_id>
[Huawei-<interface-name>]# port trunk allow-pass vlan <vlan_list>
[Huawei-<interface-name>]# port hybrid pvid vlan <vlan_id>
[Huawei-<interface-name>]# port hybrid untagged vlan <vlan_list>

### VLAN维护

[Huawei] display vlan
[Huawei] display vlan <vlan_id>
[Huawei] display port vlan

---

## 二、链路聚合命令（Eth-Trunk）

### 创建Eth-Trunk接口

<Huawei> system-view
[Huawei] interface Eth-Trunk 10
[Huawei-Eth-Trunk10]# port link-type trunk
[Huawei-Eth-Trunk10]# port trunk allow-pass vlan all
[Huawei-Eth-Trunk10]# quit

### 将物理接口加入Eth-Trunk

[Huawei] interface GigabitEthernet 0/0/1
[Huawei-GigabitEthernet0/0/1]# eth-trunk 10
[Huawei-GigabitEthernet0/0/1]# quit

[Huawei] interface GigabitEthernet 0/0/2
[Huawei-GigabitEthernet0/0/2]# eth-trunk 10
[Huawei-GigabitEthernet0/0/2]# quit

### 配置LACP模式

[Huawei] interface Eth-Trunk 10
[Huawei-Eth-Trunk10]# mode lacp
[Huawei-Eth-Trunk10]# quit

### 聚合维护命令

[Huawei] display eth-trunk <trunk-id>
[Huawei] display eth-trunk <trunk-id> brief
[Huawei] display lacp statistics eth-trunk <trunk-id>

---

## 三、路由配置命令

### 静态路由

[Huawei] ip route-static <dest-address> {mask | mask-length} <next-hop-address> [preference <value>]
[Huawei] ip route-static 0.0.0.0 0.0.0.0 <next-hop-address>

**配置示例**：

[Huawei] ip route-static 192.168.100.0 255.255.255.0 192.168.1.1
[Huawei] ip route-static 0.0.0.0 0.0.0.0 192.168.1.254

### VLAN接口IP配置

[Huawei] interface Vlanif 100
[Huawei-Vlanif100]# ip address 192.168.100.1 255.255.255.0
[Huawei-Vlanif100]# quit

### 路由维护

[Huawei] display ip routing-table
[Huawei] display ip routing-table verbose
[Huawei] display ip interface brief

---

## 四、系统与基础接口配置

### 系统管理

<Huawei> system-view
[Huawei] sysname <hostname>
[Huawei] user-interface console 0
[Huawei-ui-console0]# authentication-mode aaa
[Huawei] user-interface vty 0 4
[Huawei-ui-vty0-4]# set authentication password cipher <password>
[Huawei] save
[Huawei] display current-configuration
[Huawei] display saved-configuration

### 接口管理

[Huawei] interface <interface-type> <interface-number>
[Huawei-<interface-name>]# description <description-text>
[Huawei-<interface-name>]# undo shutdown
[Huawei-<interface-name>]# speed {10 | 100 | 1000 | auto}
[Huawei-<interface-name>]# duplex {full | half | auto}
[Huawei-<interface-name>]# ip address <ip-address> <mask>
[Huawei-<interface-name>]# undo ip address

### DHCP服务

[Huawei] dhcp enable
[Huawei] ip pool VLAN100
[Huawei-ip-pool-VLAN100]# network 192.168.100.0 mask 255.255.255.0
[Huawei-ip-pool-VLAN100]# gateway-list 192.168.100.1
[Huawei-ip-pool-VLAN100]# dns-list 8.8.8.8 114.114.114.114
[Huawei-ip-pool-VLAN100]# lease day 7

---

## 五、通用维护命令

<Huawei> display version
<Huawei> display device
<Huawei> display interface brief
<Huawei> display interface <interface-name>
<Huawei> display cpu-usage
<Huawei> display memory-usage
<Huawei> display logbuffer
<Huawei> display arp
<Huawei> display mac-address

---

## 六、系统操作

<Huawei> reset saved-configuration
<Huawei> reboot
<Huawei> clock datetime <HH:MM:SS> <YYYY-MM-DD>
<Huawei> display clock

---

## 七、调试命令

<Huawei> ping <ip-address>
<Huawei> tracert <ip-address>
<Huawei> display ip interface brief
<Huawei> display ip routing-table
