/**
 * 智能物流管理系统 - Mock数据
 * 包含所有业务模块的模拟数据，用于原型演示
 */

// ==================== 1. 用户与角色数据 ====================

const users = [
  { id: 1, username: 'admin', password: '123456', name: '超级管理员', role: 'admin', avatar: 'A', email: 'admin@logistics.com' },
  { id: 2, username: 'manager', password: '123456', name: '张经理', role: 'manager', avatar: 'Z', email: 'zhang@logistics.com' },
  { id: 3, username: 'dispatcher', password: '123456', name: '李调度', role: 'dispatcher', avatar: 'L', email: 'li@logistics.com' },
  { id: 4, username: 'service', password: '123456', name: '王客服', role: 'service', avatar: 'W', email: 'wang@logistics.com' },
  { id: 5, username: 'warehouse', password: '123456', name: '赵仓管', role: 'warehouse', avatar: 'Z', email: 'zhao@logistics.com' },
  { id: 6, username: 'driver1', password: '123456', name: '钱师傅', role: 'driver', avatar: 'Q', email: 'qian@logistics.com' }
];

const roles = [
  { id: 'admin', name: '超级管理员', permissions: ['all'] },
  { id: 'manager', name: '物流经理', permissions: ['home', 'dashboard', 'exception', 'system'] },
  { id: 'dispatcher', name: '调度员', permissions: ['home', 'dispatch', 'order:list', 'vehicle:list', 'driver:list', 'track'] },
  { id: 'service', name: '客服人员', permissions: ['home', 'order:list', 'order:create', 'exception:create', 'sign'] },
  { id: 'warehouse', name: '仓库管理员', permissions: ['home', 'order:list', 'track', 'sign'] },
  { id: 'driver', name: '司机', permissions: ['home', 'track', 'exception:create'] }
];

// ==================== 2. 导航菜单数据 ====================

const menus = [
  {
    id: 'home',
    name: '首页',
    icon: 'home',
    path: '/home',
    roles: ['all']
  },
  {
    id: 'order',
    name: '订单管理',
    icon: 'file-text',
    path: '/order/list',
    roles: ['admin', 'manager', 'dispatcher', 'service', 'warehouse'],
    children: [
      { id: 'order-list', name: '订单列表', path: '/order/list', roles: ['admin', 'manager', 'dispatcher', 'service', 'warehouse'] },
      { id: 'order-create', name: '新建订单', path: '/order/create', roles: ['admin', 'dispatcher', 'service'] }
    ]
  },
  {
    id: 'vehicle',
    name: '车辆管理',
    icon: 'truck',
    path: '/vehicle/list',
    roles: ['admin', 'manager', 'dispatcher'],
    children: [
      { id: 'vehicle-list', name: '车辆列表', path: '/vehicle/list', roles: ['admin', 'manager', 'dispatcher'] },
      { id: 'vehicle-create', name: '新增车辆', path: '/vehicle/create', roles: ['admin', 'dispatcher'] }
    ]
  },
  {
    id: 'driver',
    name: '司机管理',
    icon: 'users',
    path: '/driver/list',
    roles: ['admin', 'manager', 'dispatcher'],
    children: [
      { id: 'driver-list', name: '司机列表', path: '/driver/list', roles: ['admin', 'manager', 'dispatcher'] },
      { id: 'driver-create', name: '新增司机', path: '/driver/create', roles: ['admin', 'dispatcher'] }
    ]
  },
  {
    id: 'dispatch',
    name: '智能调度',
    icon: 'send',
    path: '/dispatch/index',
    roles: ['admin', 'manager', 'dispatcher']
  },
  {
    id: 'track',
    name: '运输轨迹',
    icon: 'map-pin',
    path: '/track/index',
    roles: ['all']
  },
  {
    id: 'exception',
    name: '异常处理',
    icon: 'alert-triangle',
    path: '/exception/list',
    roles: ['admin', 'manager', 'dispatcher', 'service', 'driver']
  },
  {
    id: 'sign',
    name: '签收回单',
    icon: 'check-circle',
    path: '/sign/list',
    roles: ['admin', 'service', 'warehouse']
  },
  {
    id: 'dashboard',
    name: '数据看板',
    icon: 'bar-chart-2',
    path: '/dashboard/index',
    roles: ['admin', 'manager', 'dispatcher']
  },
  {
    id: 'system',
    name: '系统设置',
    icon: 'settings',
    path: '/system/index',
    roles: ['admin'],
    children: [
      { id: 'system-user', name: '用户管理', path: '/system/user', roles: ['admin'] },
      { id: 'system-role', name: '角色权限', path: '/system/role', roles: ['admin'] },
      { id: 'system-log', name: '操作日志', path: '/system/log', roles: ['admin', 'manager'] }
    ]
  }
];

// ==================== 3. 首页核心指标 ====================

const homepageMetrics = {
  todayOrders: 156,
  transportOrders: 42,
  warningCount: 3,
  vehicleUsage: 78,
  pendingDispatch: 12,
  pendingApprove: 3,
  pendingSign: 8,
  totalVehicles: 45,
  availableVehicles: 28,
  totalDrivers: 52,
  availableDrivers: 35
};

// 首页待办事项
const todoItems = [
  { id: 1, type: 'pendingDispatch', title: '待派单订单', count: 12, route: '/order/list?status=pending', priority: 1 },
  { id: 2, type: 'pendingApprove', title: '待审批异常', count: 3, route: '/exception/list?status=pending', priority: 1 },
  { id: 3, type: 'pendingSign', title: '待确认签收', count: 8, route: '/sign/list?status=pending', priority: 2 }
];

// 首页快捷操作
const quickActions = [
  { key: 'newOrder', name: '新建订单', icon: 'plus', route: '/order/create', roles: ['dispatcher', 'service'] },
  { key: 'dispatch', name: '快速调度', icon: 'truck', route: '/dispatch/index', roles: ['dispatcher'] },
  { key: 'exception', name: '异常处理', icon: 'alert-triangle', route: '/exception/list', roles: ['dispatcher', 'service'] },
  { key: 'dashboard', name: '数据看板', icon: 'bar-chart-2', route: '/dashboard/index', roles: ['admin', 'manager'] },
  { key: 'track', name: '运输追踪', icon: 'map-pin', route: '/track/index', roles: ['all'] }
];

// 首页趋势数据
const trendData = {
  dates: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  orders: [120, 145, 132, 156, 148, 165, 156],
  transport: [35, 42, 38, 45, 40, 48, 42],
  completed: [30, 38, 35, 42, 38, 45, 40]
};

// ==================== 4. 订单数据 (20+条) ====================

const orders = [
  {
    id: 1, orderNo: 'LOG202401150001', customerName: '北京华夏科技', status: 'pending',
    shipperCity: '北京', consigneeCity: '上海', goodsName: '电子产品', goodsWeight: 500,
    requiredTime: '2024-01-16 18:00:00', createTime: '2024-01-15 09:30:00',
    senderName: '李先生', senderContact: '13800138001', senderAddress: '北京市朝阳区望京SOHO',
    receiverName: '王女士', receiverContact: '13600136001', receiverAddress: '上海市浦东新区张江路'
  },
  {
    id: 2, orderNo: 'LOG202401150002', customerName: '上海德邦物流', status: 'dispatched',
    shipperCity: '上海', consigneeCity: '广州', goodsName: '服装面料', goodsWeight: 1200,
    requiredTime: '2024-01-17 12:00:00', createTime: '2024-01-15 10:15:00',
    driverName: '钱师傅', driverPhone: '13900139001', vehicleNo: '沪A12345',
    senderName: '张经理', senderContact: '13700137001', senderAddress: '上海市嘉定区工业园',
    receiverName: '陈总', receiverContact: '13500135001', receiverAddress: '广州市白云区人和镇'
  },
  {
    id: 3, orderNo: 'LOG202401150003', customerName: '广州顺达商贸', status: 'in_transit',
    shipperCity: '广州', consigneeCity: '深圳', goodsName: '日用品', goodsWeight: 800,
    requiredTime: '2024-01-15 20:00:00', createTime: '2024-01-15 11:00:00',
    driverName: '孙师傅', driverPhone: '13900139002', vehicleNo: '粤B67890',
    senderName: '刘女士', senderContact: '13800138002', senderAddress: '广州市天河区珠江新城',
    receiverName: '周先生', receiverContact: '13600136002', receiverAddress: '深圳市南山区科技园'
  },
  {
    id: 4, orderNo: 'LOG202401150004', customerName: '深圳华强电子', status: 'in_transit',
    shipperCity: '深圳', consigneeCity: '成都', goodsName: '电子元器件', goodsWeight: 300,
    requiredTime: '2024-01-16 15:00:00', createTime: '2024-01-15 08:45:00',
    driverName: '吴师傅', driverPhone: '13900139003', vehicleNo: '川C11111',
    senderName: '郑经理', senderContact: '13700137002', senderAddress: '深圳市福田区华强北',
    receiverName: '冯女士', receiverContact: '13500135002', receiverAddress: '成都市高新区天府大道'
  },
  {
    id: 5, orderNo: 'LOG202401150005', customerName: '成都川蜀贸易', status: 'arrived',
    shipperCity: '成都', consigneeCity: '重庆', goodsName: '食品调料', goodsWeight: 600,
    requiredTime: '2024-01-15 14:00:00', createTime: '2024-01-15 07:30:00',
    driverName: '赵师傅', driverPhone: '13900139004', vehicleNo: '渝D22222',
    senderName: '何先生', senderContact: '13800138003', senderAddress: '成都市武侯区浆洗街',
    receiverName: '许女士', receiverContact: '13600136003', receiverAddress: '重庆市渝北区新南路'
  },
  {
    id: 6, orderNo: 'LOG202401150006', customerName: '武汉长江物流', status: 'in_transit',
    shipperCity: '武汉', consigneeCity: '长沙', goodsName: '五金工具', goodsWeight: 1500,
    requiredTime: '2024-01-16 10:00:00', createTime: '2024-01-15 12:00:00',
    driverName: '冯师傅', driverPhone: '13900139005', vehicleNo: '鄂E33333',
    senderName: '蒋经理', senderContact: '13700137003', senderAddress: '武汉市江汉区解放大道',
    receiverName: '韩女士', receiverContact: '13500135003', receiverAddress: '长沙市岳麓区麓山南路'
  },
  {
    id: 7, orderNo: 'LOG202401140007', customerName: '南京金陵货运', status: 'completed',
    shipperCity: '南京', consigneeCity: '杭州', goodsName: '办公设备', goodsWeight: 450,
    requiredTime: '2024-01-15 18:00:00', createTime: '2024-01-14 09:00:00',
    driverName: '丁师傅', driverPhone: '13900139006', vehicleNo: '苏F44444',
    senderName: '丁经理', senderContact: '13800138004', senderAddress: '南京市鼓楼区中山路',
    receiverName: '唐女士', receiverContact: '13600136004', receiverAddress: '杭州市西湖区文三路'
  },
  {
    id: 8, orderNo: 'LOG202401140008', customerName: '杭州阿里巴巴', status: 'completed',
    shipperCity: '杭州', consigneeCity: '宁波', goodsName: '纺织品', goodsWeight: 900,
    requiredTime: '2024-01-15 16:00:00', createTime: '2024-01-14 14:30:00',
    driverName: '唐师傅', driverPhone: '13900139007', vehicleNo: '浙G55555',
    senderName: '沈经理', senderContact: '13700137004', senderAddress: '杭州市滨江区江南大道',
    receiverName: '卢女士', receiverContact: '13500135004', receiverAddress: '宁波市鄞州区天童路'
  },
  {
    id: 9, orderNo: 'LOG202401140009', customerName: '西安西北物流', status: 'cancelled',
    shipperCity: '西安', consigneeCity: '兰州', goodsName: '化工原料', goodsWeight: 2000,
    requiredTime: '2024-01-15 20:00:00', createTime: '2024-01-14 16:00:00',
    cancelReason: '客户取消订单'
  },
  {
    id: 10, orderNo: 'LOG202401130010', customerName: '郑州中原货运', status: 'completed',
    shipperCity: '郑州', consigneeCity: '济南', goodsName: '机械设备', goodsWeight: 1800,
    requiredTime: '2024-01-14 18:00:00', createTime: '2024-01-13 10:00:00',
    driverName: '范师傅', driverPhone: '13900139008', vehicleNo: '豫H66666',
    senderName: '苏经理', senderContact: '13800138005', senderAddress: '郑州市二七区二马路',
    receiverName: '汪女士', receiverContact: '13600136005', receiverAddress: '济南市历下区泉城路'
  },
  {
    id: 11, orderNo: 'LOG202401150011', customerName: '天津港务集团', status: 'pending',
    shipperCity: '天津', consigneeCity: '青岛', goodsName: '塑料原料', goodsWeight: 2500,
    requiredTime: '2024-01-17 08:00:00', createTime: '2024-01-15 14:00:00',
    senderName: '袁经理', senderContact: '13700137005', senderAddress: '天津市滨海新区港城大道',
    receiverName: '龚女士', receiverContact: '13500135005', receiverAddress: '青岛市黄岛区黄河东路'
  },
  {
    id: 12, orderNo: 'LOG202401150012', customerName: '沈阳东北物流', status: 'in_transit',
    shipperCity: '沈阳', consigneeCity: '大连', goodsName: '钢材建材', goodsWeight: 3500,
    requiredTime: '2024-01-16 12:00:00', createTime: '2024-01-15 08:00:00',
    driverName: '姜师傅', driverPhone: '13900139009', vehicleNo: '辽J77777',
    senderName: '卢经理', senderContact: '13800138006', senderAddress: '沈阳市铁西区重工街',
    receiverName: '白女士', receiverContact: '13600136006', receiverAddress: '大连市甘井子区华北路'
  },
  {
    id: 13, orderNo: 'LOG202401140013', customerName: '哈尔滨北国货运', status: 'completed',
    shipperCity: '哈尔滨', consigneeCity: '长春', goodsName: '粮食作物', goodsWeight: 5000,
    requiredTime: '2024-01-15 16:00:00', createTime: '2024-01-14 11:00:00',
    driverName: '常师傅', driverPhone: '13900139010', vehicleNo: '黑K88888',
    senderName: '毛经理', senderContact: '13700137006', senderAddress: '哈尔滨市香坊区公滨路',
    receiverName: '金女士', receiverContact: '13500135006', receiverAddress: '长春市绿园区春城大街'
  },
  {
    id: 14, orderNo: 'LOG202401150014', customerName: '福州东南物流', status: 'pending',
    shipperCity: '福州', consigneeCity: '厦门', goodsName: '工艺品', goodsWeight: 200,
    requiredTime: '2024-01-16 14:00:00', createTime: '2024-01-15 15:30:00',
    senderName: '毛经理', senderContact: '13800138007', senderAddress: '福州市鼓楼区五一路',
    receiverName: '钟女士', receiverContact: '13600136007', receiverAddress: '厦门市思明区鹭江道'
  },
  {
    id: 15, orderNo: 'LOG202401130015', customerName: '南昌赣江货运', status: 'completed',
    shipperCity: '南昌', consigneeCity: '合肥', goodsName: '有色金属', goodsWeight: 2800,
    requiredTime: '2024-01-14 20:00:00', createTime: '2024-01-13 13:00:00',
    driverName: '秦师傅', driverPhone: '13900139011', vehicleNo: '赣L99999',
    senderName: '汤经理', senderContact: '13700137007', senderAddress: '南昌市西湖区八一大道',
    receiverName: '程女士', receiverContact: '13500135007', receiverAddress: '合肥市庐阳区长江中路'
  },
  {
    id: 16, orderNo: 'LOG202401150016', customerName: '昆明西南物流', status: 'in_transit',
    shipperCity: '昆明', consigneeCity: '贵阳', goodsName: '鲜花绿植', goodsWeight: 350,
    requiredTime: '2024-01-15 22:00:00', createTime: '2024-01-15 06:00:00',
    driverName: '孔师傅', driverPhone: '13900139012', vehicleNo: '云M00000',
    senderName: '赖经理', senderContact: '13800138008', senderAddress: '昆明市呈贡区彩云路',
    receiverName: '夏女士', receiverContact: '13600136008', receiverAddress: '贵阳市南明区中华南路'
  },
  {
    id: 17, orderNo: 'LOG202401140017', customerName: '南宁桂越货运', status: 'completed',
    shipperCity: '南宁', consigneeCity: '海口', goodsName: '水果蔬菜', goodsWeight: 1500,
    requiredTime: '2024-01-15 10:00:00', createTime: '2024-01-14 08:00:00',
    driverName: '施师傅', driverPhone: '13900139013', vehicleNo: '桂N11111',
    senderName: '葛经理', senderContact: '13700137008', senderAddress: '南宁市青秀区民族大道',
    receiverName: '聂女士', receiverContact: '13500135008', receiverAddress: '海口市龙华区海秀路'
  },
  {
    id: 18, orderNo: 'LOG202401150018', customerName: '拉萨高原物流', status: 'exception',
    shipperCity: '拉萨', consigneeCity: '西宁', goodsName: '藏毯挂毯', goodsWeight: 180,
    requiredTime: '2024-01-18 18:00:00', createTime: '2024-01-15 16:00:00',
    driverName: '鲁师傅', driverPhone: '13900139014', vehicleNo: '藏O22222',
    exceptionType: '运输延迟', exceptionDesc: '青藏线天气恶劣，道路封闭',
    senderName: '邢经理', senderContact: '13800138009', senderAddress: '拉萨市城关区北京路',
    receiverName: '谭女士', receiverContact: '13600136009', receiverAddress: '西宁市城西区胜利路'
  },
  {
    id: 19, orderNo: 'LOG202401140019', customerName: '乌鲁木齐西北', status: 'completed',
    shipperCity: '乌鲁木齐', consigneeCity: '兰州', goodsName: '干果特产', goodsWeight: 600,
    requiredTime: '2024-01-16 12:00:00', createTime: '2024-01-14 10:30:00',
    driverName: '兰师傅', driverPhone: '13900139015', vehicleNo: '新P33333',
    senderName: '岳经理', senderContact: '13700137009', senderAddress: '乌鲁木齐市天山区中山路',
    receiverName: '卓女士', receiverContact: '13500135009', receiverAddress: '兰州市城关区东方红广场'
  },
  {
    id: 20, orderNo: 'LOG202401150020', customerName: '呼和浩特物流', status: 'pending',
    shipperCity: '呼和浩特', consigneeCity: '银川', goodsName: '羊绒制品', goodsWeight: 280,
    requiredTime: '2024-01-17 16:00:00', createTime: '2024-01-15 17:00:00',
    senderName: '齐经理', senderContact: '13800138010', senderAddress: '呼和浩特市新城区新华大街',
    receiverName: '杜女士', receiverContact: '13600136010', receiverAddress: '银川市兴庆区解放街'
  },
  {
    id: 21, orderNo: 'LOG202401130021', customerName: '石家庄中转站', status: 'completed',
    shipperCity: '石家庄', consigneeCity: '太原', goodsName: '煤炭物资', goodsWeight: 8000,
    requiredTime: '2024-01-14 20:00:00', createTime: '2024-01-13 15:00:00',
    driverName: '元师傅', driverPhone: '13900139016', vehicleNo: '冀Q44444',
    senderName: '山经理', senderContact: '13700137010', senderAddress: '石家庄市桥西区裕华路',
    receiverName: '武女士', receiverContact: '13500135010', receiverAddress: '太原市迎泽区迎泽大街'
  },
  {
    id: 22, orderNo: 'LOG202401150022', customerName: '济南齐鲁物流', status: 'in_transit',
    shipperCity: '济南', consigneeCity: '天津', goodsName: '医药用品', goodsWeight: 420,
    requiredTime: '2024-01-15 19:00:00', createTime: '2024-01-15 13:00:00',
    driverName: '贝师傅', driverPhone: '13900139017', vehicleNo: '鲁R55555',
    savename: '钮经理', senderContact: '13800138011', senderAddress: '济南市历下区泉城路',
    receiverName: '卞女士', receiverContact: '13600136011', receiverAddress: '天津市南开区卫津路'
  }
];

// 订单状态映射
const orderStatusMap = {
  pending: { text: '待派单', color: '#1890ff' },
  dispatched: { text: '已派单', color: '#13c2c2' },
  in_transit: { text: '运输中', color: '#fa8c16' },
  arrived: { text: '已到达', color: '#722ed1' },
  completed: { text: '已完成', color: '#52c41a' },
  cancelled: { text: '已取消', color: '#8c8c8c' },
  exception: { text: '异常', color: '#f5222d' }
};

// ==================== 5. 车辆数据 (15+条) ====================

const vehicles = [
  { id: 1, plateNumber: '京A12345', vehicleType: '大型货车', loadCapacity: 20, companyName: '北京一队', status: 'transporting', gpsDeviceNo: 'GPS001', currentCity: '上海', createTime: '2023-01-15 10:00:00' },
  { id: 2, plateNumber: '京B67890', vehicleType: '中型货车', loadCapacity: 10, companyName: '北京一队', status: 'idle', gpsDeviceNo: 'GPS002', currentCity: '北京', createTime: '2023-02-20 10:00:00' },
  { id: 3, plateNumber: '沪C11111', vehicleType: '大型货车', loadCapacity: 25, companyName: '上海一队', status: 'transporting', gpsDeviceNo: 'GPS003', currentCity: '广州', createTime: '2023-03-10 10:00:00' },
  { id: 4, plateNumber: '粤B22222', vehicleType: '小型货车', loadCapacity: 5, companyName: '深圳一队', status: 'idle', gpsDeviceNo: 'GPS004', currentCity: '深圳', createTime: '2023-04-05 10:00:00' },
  { id: 5, plateNumber: '川D33333', vehicleType: '中型货车', loadCapacity: 12, companyName: '成都一队', status: 'transporting', gpsDeviceNo: 'GPS005', currentCity: '成都', createTime: '2023-05-18 10:00:00' },
  { id: 6, plateNumber: '浙E44444', vehicleType: '大型货车', loadCapacity: 30, companyName: '杭州一队', status: 'maintaining', gpsDeviceNo: 'GPS006', currentCity: '杭州', createTime: '2023-06-22 10:00:00' },
  { id: 7, plateNumber: '鄂F55555', vehicleType: '中型货车', loadCapacity: 15, companyName: '武汉一队', status: 'idle', gpsDeviceNo: 'GPS007', currentCity: '武汉', createTime: '2023-07-30 10:00:00' },
  { id: 8, plateNumber: '苏G66666', vehicleType: '大型货车', loadCapacity: 20, companyName: '南京一队', status: 'offline', gpsDeviceNo: '', currentCity: '南京', createTime: '2023-08-12 10:00:00' },
  { id: 9, plateNumber: '豫H77777', vehicleType: '重型货车', loadCapacity: 40, companyName: '郑州一队', status: 'transporting', gpsDeviceNo: 'GPS008', currentCity: '济南', createTime: '2023-09-05 10:00:00' },
  { id: 10, plateNumber: '津J88888', vehicleType: '中型货车', loadCapacity: 12, companyName: '天津一队', status: 'idle', gpsDeviceNo: 'GPS009', currentCity: '天津', createTime: '2023-10-18 10:00:00' },
  { id: 11, plateNumber: '辽K99999', vehicleType: '大型货车', loadCapacity: 25, companyName: '沈阳一队', status: 'transporting', gpsDeviceNo: 'GPS010', currentCity: '大连', createTime: '2023-11-25 10:00:00' },
  { id: 12, plateNumber: '黑L00000', vehicleType: '中型货车', loadCapacity: 10, companyName: '哈尔滨一队', status: 'idle', gpsDeviceNo: 'GPS011', currentCity: '长春', createTime: '2023-12-08 10:00:00' },
  { id: 13, plateNumber: '云M11111', vehicleType: '小型货车', loadCapacity: 3, companyName: '昆明一队', status: 'transporting', gpsDeviceNo: 'GPS012', currentCity: '贵阳', createTime: '2024-01-05 10:00:00' },
  { id: 14, plateNumber: '桂N22222', vehicleType: '中型货车', loadCapacity: 15, companyName: '南宁一队', status: 'idle', gpsDeviceNo: 'GPS013', currentCity: '海口', createTime: '2024-01-10 10:00:00' },
  { id: 15, plateNumber: '新P33333', vehicleType: '大型货车', loadCapacity: 22, companyName: '新疆一队', status: 'transporting', gpsDeviceNo: 'GPS014', currentCity: '兰州', createTime: '2024-01-12 10:00:00' }
];

// 车辆状态映射
const vehicleStatusMap = {
  idle: { text: '空闲', color: '#52c41a' },
  transporting: { text: '运输中', color: '#1890ff' },
  maintaining: { text: '维修中', color: '#fa8c16' },
  offline: { text: '离线', color: '#d9d9d9' }
};

// ==================== 6. 司机数据 (20+条) ====================

const drivers = [
  { id: 1, name: '张伟', phone: '13800138001', driveType: 'A2', fleetName: '北京一队', vehicleNo: '京A12345', status: 'transporting', hireDate: '2023-01-15', driverLicense: '110101199001011234', rating: 4.9 },
  { id: 2, name: '李强', phone: '13800138002', driveType: 'A1', fleetName: '北京一队', vehicleNo: '京B67890', status: 'idle', hireDate: '2023-02-20', driverLicense: '110101199002021234', rating: 4.8 },
  { id: 3, name: '王芳', phone: '13800138003', driveType: 'B1', fleetName: '上海一队', vehicleNo: '沪C11111', status: 'transporting', hireDate: '2023-03-10', driverLicense: '310101199003031234', rating: 4.7 },
  { id: 4, name: '赵磊', phone: '13800138004', driveType: 'A2', fleetName: '深圳一队', vehicleNo: '粤B22222', status: 'idle', hireDate: '2023-04-05', driverLicense: '440301199004041234', rating: 4.9 },
  { id: 5, name: '陈静', phone: '13800138005', driveType: 'B2', fleetName: '成都一队', vehicleNo: '川D33333', status: 'transporting', hireDate: '2023-05-18', driverLicense: '510101199005051234', rating: 4.6 },
  { id: 6, name: '刘洋', phone: '13800138006', driveType: 'A1', fleetName: '杭州一队', vehicleNo: '浙E44444', status: 'onLeave', hireDate: '2023-06-22', driverLicense: '330101199006061234', rating: 4.8 },
  { id: 7, name: '杨涛', phone: '13800138007', driveType: 'A2', fleetName: '武汉一队', vehicleNo: '鄂F55555', status: 'idle', hireDate: '2023-07-30', driverLicense: '420101199007071234', rating: 4.7 },
  { id: 8, name: '周敏', phone: '13800138008', driveType: 'B1', fleetName: '南京一队', vehicleNo: '苏G66666', status: 'idle', hireDate: '2023-08-12', driverLicense: '320101199008081234', rating: 4.5 },
  { id: 9, name: '吴志强', phone: '13800138009', driveType: 'A1', fleetName: '郑州一队', vehicleNo: '豫H77777', status: 'transporting', hireDate: '2023-09-05', driverLicense: '410101199009091234', rating: 4.9 },
  { id: 10, name: '黄莉', phone: '13800138010', driveType: 'B2', fleetName: '天津一队', vehicleNo: '津J88888', status: 'idle', hireDate: '2023-10-18', driverLicense: '120101199010101234', rating: 4.8 },
  { id: 11, name: '钱七', phone: '13800138011', driveType: 'C1', fleetName: '沈阳一队', vehicleNo: '辽K99999', status: 'transporting', hireDate: '2023-11-25', driverLicense: '210101199011111234', rating: 4.6 },
  { id: 12, name: '孙八', phone: '13800138012', driveType: 'A2', fleetName: '哈尔滨一队', vehicleNo: '黑L00000', status: 'idle', hireDate: '2023-12-08', driverLicense: '230101199012121234', rating: 4.7 },
  { id: 13, name: '周九', phone: '13800138013', driveType: 'B1', fleetName: '昆明一队', vehicleNo: '云M11111', status: 'transporting', hireDate: '2024-01-05', driverLicense: '530101200001011234', rating: 4.8 },
  { id: 14, name: '吴十', phone: '13800138014', driveType: 'B2', fleetName: '南宁一队', vehicleNo: '桂N22222', status: 'idle', hireDate: '2024-01-10', driverLicense: '450101200002021234', rating: 4.5 },
  { id: 15, name: '郑十一', phone: '13800138015', driveType: 'A1', fleetName: '新疆一队', vehicleNo: '新P33333', status: 'transporting', hireDate: '2024-01-12', driverLicense: '650101200003031234', rating: 4.9 },
  { id: 16, name: '王十二', phone: '13800138016', driveType: 'A2', fleetName: '北京一队', vehicleNo: '', status: 'idle', hireDate: '2024-01-14', driverLicense: '110101200004041234', rating: 4.7 },
  { id: 17, name: '刘十三', phone: '13800138017', driveType: 'B1', fleetName: '上海一队', vehicleNo: '', status: 'idle', hireDate: '2024-01-15', driverLicense: '310101200005051234', rating: 4.6 },
  { id: 18, name: '陈十四', phone: '13800138018', driveType: 'C1', fleetName: '广州一队', vehicleNo: '', status: 'onLeave', hireDate: '2024-01-16', driverLicense: '440101200006061234', rating: 4.8 },
  { id: 19, name: '杨十五', phone: '13800138019', driveType: 'A2', fleetName: '深圳一队', vehicleNo: '', status: 'idle', hireDate: '2024-01-17', driverLicense: '440301200007071234', rating: 4.7 },
  { id: 20, name: '赵十六', phone: '13800138020', driveType: 'B2', fleetName: '成都一队', vehicleNo: '', status: 'idle', hireDate: '2024-01-18', driverLicense: '510101200008081234', rating: 4.9 }
];

// 司机状态映射
const driverStatusMap = {
  idle: { text: '空闲', color: '#52c41a' },
  transporting: { text: '运输中', color: '#fa8c16' },
  onLeave: { text: '请假', color: '#d9d9d9' }
};

// ==================== 7. 智能调度数据 ====================

// 待派单订单（从订单中筛选status=pending）
const pendingOrders = orders.filter(o => o.status === 'pending');

// 可用车辆
const availableVehicles = vehicles.filter(v => v.status === 'idle');

// 可用司机
const availableDrivers = drivers.filter(d => d.status === 'idle');

// 派单历史
const dispatchHistory = [
  { id: 1, dispatchNo: 'PD202401150001', orderNo: 'LOG202401150002', vehicleNo: '沪A12345', driverName: '钱师傅', dispatchTime: '2024-01-15 10:30:00', dispatchType: 'smart' },
  { id: 2, dispatchNo: 'PD202401150002', orderNo: 'LOG202401150003', vehicleNo: '粤B67890', driverName: '孙师傅', dispatchTime: '2024-01-15 11:15:00', dispatchType: 'manual' },
  { id: 3, dispatchNo: 'PD202401150003', orderNo: 'LOG202401150004', vehicleNo: '川C11111', driverName: '吴师傅', dispatchTime: '2024-01-15 12:00:00', dispatchType: 'smart' },
  { id: 4, dispatchNo: 'PD202401140001', orderNo: 'LOG202401140007', vehicleNo: '苏F44444', driverName: '丁师傅', dispatchTime: '2024-01-14 09:30:00', dispatchType: 'smart' },
  { id: 5, dispatchNo: 'PD202401140002', orderNo: 'LOG202401140008', vehicleNo: '浙G55555', driverName: '唐师傅', dispatchTime: '2024-01-14 14:45:00', dispatchType: 'manual' }
];

// 调度统计
const dispatchStats = {
  todayTotal: 12,
  smartDispatch: 8,
  manualDispatch: 4,
  successRate: 98.5,
  avgDispatchTime: 2.3
};

// ==================== 8. 运输轨迹数据 ====================

// 运输任务列表
const transportTasks = [
  {
    id: 1, taskId: 'TSK202401150001', orderNo: 'LOG202401150003', vehicleNo: '粤B67890',
    driverName: '孙师傅', driverPhone: '13900139002',
    origin: '广州市天河区珠江新城', destination: '深圳市南山区科技园',
    status: 'in_transit', estimatedArrival: '2024-01-15 20:00:00',
    currentLocation: { lng: 114.057, lat: 22.543 },
    progress: 65, createdTime: '2024-01-15 11:00:00'
  },
  {
    id: 2, taskId: 'TSK202401150002', orderNo: 'LOG202401150004', vehicleNo: '川C11111',
    driverName: '吴师傅', driverPhone: '13900139003',
    origin: '深圳市福田区华强北', destination: '成都市高新区天府大道',
    status: 'in_transit', estimatedArrival: '2024-01-16 15:00:00',
    currentLocation: { lng: 108.939, lat: 30.804 },
    progress: 42, createdTime: '2024-01-15 08:45:00'
  },
  {
    id: 3, taskId: 'TSK202401150003', orderNo: 'LOG202401150005', vehicleNo: '渝D22222',
    driverName: '赵师傅', driverPhone: '13900139004',
    origin: '成都市武侯区浆洗街', destination: '重庆市渝北区新南路',
    status: 'arrived', estimatedArrival: '2024-01-15 14:00:00',
    actualArrival: '2024-01-15 13:45:00',
    progress: 100, createdTime: '2024-01-15 07:30:00'
  }
];

// 轨迹点数据（模拟一条完整轨迹）
const trackPoints = [
  { id: 1, lng: 113.264, lat: 23.129, speed: 0, address: '广州市天河区珠江新城装货点', time: '2024-01-15 11:00:00', status: '已装车' },
  { id: 2, lng: 113.326, lat: 23.185, speed: 45, address: '广州市天河区黄埔大道', time: '2024-01-15 11:30:00', status: '运输中' },
  { id: 3, lng: 113.433, lat: 23.253, speed: 60, address: '广州市萝岗区科学城', time: '2024-01-15 12:00:00', status: '运输中' },
  { id: 4, lng: 113.852, lat: 22.793, speed: 55, address: '东莞市南城区', time: '2024-01-15 13:00:00', status: '运输中' },
  { id: 5, lng: 114.057, lat: 22.543, speed: 40, address: '深圳市宝安区西乡', time: '2024-01-15 14:00:00', status: '运输中' },
  { id: 6, lng: 114.089, lat: 22.625, speed: 30, address: '深圳市南山区科苑', time: '2024-01-15 15:00:00', status: '运输中' },
  { id: 7, lng: 114.057, lat: 22.543, speed: 0, address: '深圳市南山区科技园卸货点', time: '2024-01-15 16:00:00', status: '已到达' }
];

// 里程碑时间轴
const milestones = [
  { id: 1, nodeName: '订单创建', nodeTime: '2024-01-15 09:30:00', location: '-', operator: '客服王五', status: 'finish' },
  { id: 2, nodeName: '智能派单', nodeTime: '2024-01-15 10:15:00', location: '-', operator: '调度员李四', status: 'finish' },
  { id: 3, nodeName: '已装车', nodeTime: '2024-01-15 11:00:00', location: '广州市天河区珠江新城', operator: '司机孙师傅', status: 'finish' },
  { id: 4, nodeName: '运输中', nodeTime: '2024-01-15 11:30:00', location: '广州市天河区黄埔大道', operator: '系统', status: 'process' },
  { id: 5, nodeName: '预计到达', nodeTime: '2024-01-15 20:00:00', location: '深圳市南山区科技园', operator: '-', status: 'wait' }
];

// ==================== 9. 异常处理数据 ====================

const exceptions = [
  {
    id: 1, exceptionNo: 'EXC202401150001', orderNo: 'LOG202401150018', vehicleNo: '藏O22222',
    driverName: '鲁师傅', type: '运输延迟', level: 'high',
    description: '青藏线天气恶劣，道路封闭，车辆被迫滞留格尔木',
    status: 'pending', createTime: '2024-01-15 16:30:00',
    handler: '', handlerTime: '', result: ''
  },
  {
    id: 2, exceptionNo: 'EXC202401140001', orderNo: 'LOG202401130012',
    vehicleNo: '辽J77777', driverName: '姜师傅',
    type: '车辆故障', level: 'medium',
    description: '车辆在高速行驶中爆胎，已更换备胎',
    status: 'resolved', createTime: '2024-01-14 10:00:00',
    handler: '调度员李四', handlerTime: '2024-01-14 12:30:00',
    result: '已更换备胎，继续运输，预计延误2小时'
  },
  {
    id: 3, exceptionNo: 'EXC202401130002', orderNo: 'LOG202401120005',
    vehicleNo: '沪A12345', driverName: '钱师傅',
    type: '货物异常', level: 'high',
    description: '货物在运输中部分受损，客户拒收部分货物',
    status: 'resolved', createTime: '2024-01-13 08:00:00',
    handler: '物流经理张', handlerTime: '2024-01-13 15:00:00',
    result: '已与客户协商，扣除部分运费后完成签收'
  },
  {
    id: 4, exceptionNo: 'EXC202401120001', orderNo: 'LOG202401100015',
    vehicleNo: '粤B22222', driverName: '赵师傅',
    type: '路线偏离', level: 'low',
    description: '司机因导航失误偏离路线3公里',
    status: 'resolved', createTime: '2024-01-12 14:00:00',
    handler: '调度员王', handlerTime: '2024-01-12 14:30:00',
    result: '已纠正路线，未造成延误'
  },
  {
    id: 5, exceptionNo: 'EXC202401150002', orderNo: 'LOG202401150020',
    vehicleNo: '鲁R55555', driverName: '贝师傅',
    type: '签收异常', level: 'medium',
    description: '客户反映货物外包装破损，拒签',
    status: 'processing', createTime: '2024-01-15 18:00:00',
    handler: '客服小李', handlerTime: '2024-01-15 19:00:00',
    result: '正在与客户协商赔偿方案'
  }
];

// 异常类型映射
const exceptionTypeMap = {
  '运输延迟': { color: '#faad14' },
  '车辆故障': { color: '#f5222d' },
  '货物异常': { color: '#f5222d' },
  '路线偏离': { color: '#1890ff' },
  '签收异常': { color: '#faad14' }
};

const exceptionLevelMap = {
  high: { text: '高', color: '#f5222d' },
  medium: { text: '中', color: '#faad14' },
  low: { text: '低', color: '#1890ff' }
};

const exceptionStatusMap = {
  pending: { text: '待处理', color: '#f5222d' },
  processing: { text: '处理中', color: '#faad14' },
  resolved: { text: '已解决', color: '#52c41a' }
};

// ==================== 10. 签收回单数据 ====================

const receipts = [
  {
    id: 1, orderNo: 'LOG202401150005', vehicleNo: '渝D22222',
    driverName: '赵师傅', status: 'confirmed',
    uploadTime: '2024-01-15 14:00:00', confirmTime: '2024-01-15 14:30:00',
    uploader: '司机赵师傅', confirmer: '仓管张三'
  },
  {
    id: 2, orderNo: 'LOG202401140007', vehicleNo: '苏F44444',
    driverName: '丁师傅', status: 'confirmed',
    uploadTime: '2024-01-14 18:00:00', confirmTime: '2024-01-14 18:20:00',
    uploader: '司机丁师傅', confirmer: '仓管李四'
  },
  {
    id: 3, orderNo: 'LOG202401140008', vehicleNo: '浙G55555',
    driverName: '唐师傅', status: 'pending',
    uploadTime: '2024-01-14 20:00:00', confirmTime: '',
    uploader: '司机唐师傅', confirmer: ''
  },
  {
    id: 4, orderNo: 'LOG202401150012', vehicleNo: '辽J77777',
    driverName: '姜师傅', status: 'pending',
    uploadTime: '2024-01-15 12:00:00', confirmTime: '',
    uploader: '司机姜师傅', confirmer: ''
  }
];

// ==================== 11. 数据看板统计 ====================

const dashboardStats = {
  // 运营概览
  overview: {
    totalOrders: 4856,
    monthOrders: 1245,
    todayOrders: 156,
    transportVolume: 9850,
    completionRate: 96.8,
    avgDeliveryTime: 18.5
  },
  // 订单趋势
  orderTrend: {
    dates: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    values: [145, 162, 158, 175, 168, 182, 156]
  },
  // 订单类型分布
  orderTypeDist: [
    { name: '电子产品', value: 32 },
    { name: '服装纺织', value: 25 },
    { name: '食品生鲜', value: 18 },
    { name: '建材五金', value: 15 },
    { name: '其他', value: 10 }
  ],
  // 线路热度
  routeHot: [
    { from: '北京', to: '上海', count: 256 },
    { from: '广州', to: '深圳', count: 198 },
    { from: '成都', to: '重庆', count: 156 },
    { from: '杭州', to: '宁波', count: 134 },
    { from: '武汉', to: '长沙', count: 112 }
  ],
  // 车辆统计
  vehicleStats: {
    total: 45,
    inUse: 32,
    idle: 8,
    maintaining: 3,
    offline: 2,
    usageRate: 78,
    avgMileage: 3250
  },
  // 司机统计
  driverStats: {
    total: 52,
    inService: 42,
    onLeave: 5,
    available: 35,
    avgAge: 38,
    avgRating: 4.7
  },
  // 异常统计
  exceptionStats: {
    total: 45,
    thisMonth: 12,
    resolved: 38,
    pending: 5,
    avgProcessTime: 2.5
  },
  // 财务统计
  financeStats: {
    monthRevenue: 2856000,
    avgFreight: 2280,
    collected: 2654000,
    pending: 202000
  }
};

// ==================== 12. 系统设置数据 ====================

const systemUsers = [
  { id: 1, username: 'admin', name: '超级管理员', role: '超级管理员', status: 'enabled', createTime: '2023-01-01 10:00:00', lastLogin: '2024-01-15 09:00:00' },
  { id: 2, username: 'manager', name: '张经理', role: '物流经理', status: 'enabled', createTime: '2023-02-15 10:00:00', lastLogin: '2024-01-14 16:30:00' },
  { id: 3, username: 'dispatcher', name: '李调度', role: '调度员', status: 'enabled', createTime: '2023-03-20 10:00:00', lastLogin: '2024-01-15 08:45:00' },
  { id: 4, username: 'service', name: '王客服', role: '客服人员', status: 'enabled', createTime: '2023-04-10 10:00:00', lastLogin: '2024-01-15 11:20:00' },
  { id: 5, username: 'warehouse', name: '赵仓管', role: '仓库管理员', status: 'enabled', createTime: '2023-05-05 10:00:00', lastLogin: '2024-01-14 14:00:00' },
  { id: 6, username: 'finance', name: '钱财务', role: '财务人员', status: 'enabled', createTime: '2023-06-01 10:00:00', lastLogin: '2024-01-13 10:30:00' }
];

const systemRoles = [
  { id: 'admin', name: '超级管理员', userCount: 1, permissions: ['all'], createTime: '2023-01-01' },
  { id: 'manager', name: '物流经理', userCount: 1, permissions: ['home', 'dashboard', 'exception', 'system', 'order:list', 'vehicle:list', 'driver:list', 'dispatch'], createTime: '2023-01-01' },
  { id: 'dispatcher', name: '调度员', userCount: 1, permissions: ['home', 'dispatch', 'order:list', 'vehicle:list', 'driver:list', 'track'], createTime: '2023-01-01' },
  { id: 'service', name: '客服人员', userCount: 1, permissions: ['home', 'order:list', 'order:create', 'exception:create', 'sign'], createTime: '2023-01-01' },
  { id: 'warehouse', name: '仓库管理员', userCount: 1, permissions: ['home', 'order:list', 'track', 'sign'], createTime: '2023-01-01' },
  { id: 'finance', name: '财务人员', userCount: 1, permissions: ['home', 'dashboard'], createTime: '2023-01-01' }
];

// 操作日志
const operationLogs = [
  { id: 1, user: '张经理', action: '登录系统', ip: '192.168.1.100', time: '2024-01-15 09:00:00', detail: '用户登录成功' },
  { id: 2, user: '李调度', action: '智能派单', ip: '192.168.1.101', time: '2024-01-15 10:30:00', detail: '订单LOG202401150002已派单' },
  { id: 3, user: '王客服', action: '新建订单', ip: '192.168.1.102', time: '2024-01-15 11:15:00', detail: '创建订单LOG202401150011' },
  { id: 4, user: '张经理', action: '异常处理', ip: '192.168.1.100', time: '2024-01-15 14:00:00', detail: '处理异常EXC202401130002' },
  { id: 5, user: '李调度', action: '修改派单', ip: '192.168.1.101', time: '2024-01-15 15:30:00', detail: '调整订单LOG202401150004派单' }
];

// 系统参数
const systemParams = [
  { id: 1, paramKey: 'dispatch.auto', paramName: '智能派单', paramValue: 'true', description: '是否启用智能派单功能' },
  { id: 2, paramKey: 'exception.threshold.delay', paramName: '延迟预警阈值', paramValue: '2', description: '运输延迟超过X小时触发预警(小时)' },
  { id: 3, paramKey: 'exception.threshold.offline', paramName: '离线预警时长', paramValue: '30', description: 'GPS离线超过X分钟触发预警(分钟)' },
  { id: 4, paramKey: 'order.timeout', paramName: '订单超时时间', paramValue: '72', description: '订单未派单超时时间(小时)' },
  { id: 5, paramKey: 'track.refresh.interval', paramName: '轨迹刷新间隔', paramValue: '30', description: '实时轨迹刷新间隔(秒)' }
];

// ==================== 13. 消息通知数据 ====================

const messages = [
  { id: 1, type: 'order', title: '新订单提醒', content: '客户北京华夏科技提交了新订单', time: '2024-01-15 09:30:00', read: false },
  { id: 2, type: 'exception', title: '异常预警', content: '订单LOG202401150018运输延迟，请及时处理', time: '2024-01-15 16:30:00', read: false },
  { id: 3, type: 'dispatch', title: '派单成功', content: '订单LOG202401150002已成功派单', time: '2024-01-15 10:30:00', read: true },
  { id: 4, type: 'sign', title: '签收提醒', content: '订单LOG202401150005已到达目的地，待签收确认', time: '2024-01-15 14:00:00', read: false },
  { id: 5, type: 'system', title: '系统通知', content: '系统将于今晚23:00进行例行维护', time: '2024-01-15 18:00:00', read: true }
];

// ==================== 导出所有数据 ====================

window.mockData = {
  // 用户与角色
  users,
  roles,
  
  // 导航菜单
  menus,
  
  // 首页数据
  homepageMetrics,
  todoItems,
  quickActions,
  trendData,
  
  // 订单数据
  orders,
  orderStatusMap,
  
  // 车辆数据
  vehicles,
  vehicleStatusMap,
  
  // 司机数据
  drivers,
  driverStatusMap,
  
  // 调度数据
  pendingOrders,
  availableVehicles,
  availableDrivers,
  dispatchHistory,
  dispatchStats,
  
  // 轨迹数据
  transportTasks,
  trackPoints,
  milestones,
  
  // 异常数据
  exceptions,
  exceptionTypeMap,
  exceptionLevelMap,
  exceptionStatusMap,
  
  // 签收回单
  receipts,
  
  // 数据看板
  dashboardStats,
  
  // 系统设置
  systemUsers,
  systemRoles,
  operationLogs,
  systemParams,
  
  // 消息通知
  messages
};

// 辅助函数
window.mockDataUtils = {
  // 获取用户信息
  getUserByUsername(username) {
    return users.find(u => u.username === username);
  },
  
  // 获取订单状态信息
  getOrderStatusInfo(status) {
    return orderStatusMap[status] || { text: '未知', color: '#999' };
  },
  
  // 获取车辆状态信息
  getVehicleStatusInfo(status) {
    return vehicleStatusMap[status] || { text: '未知', color: '#999' };
  },
  
  // 获取司机状态信息
  getDriverStatusInfo(status) {
    return driverStatusMap[status] || { text: '未知', color: '#999' };
  },
  
  // 获取异常类型信息
  getExceptionTypeInfo(type) {
    return exceptionTypeMap[type] || { color: '#999' };
  },
  
  // 获取异常级别信息
  getExceptionLevelInfo(level) {
    return exceptionLevelMap[level] || { text: '未知', color: '#999' };
  },
  
  // 获取异常状态信息
  getExceptionStatusInfo(status) {
    return exceptionStatusMap[status] || { text: '未知', color: '#999' };
  },
  
  // 格式化日期时间
  formatDateTime(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  },
  
  // 格式化日期
  formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN');
  },
  
  // 手机号脱敏
  maskPhone(phone) {
    if (!phone) return '-';
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
  },
  
  // 身份证脱敏
  maskIdCard(idCard) {
    if (!idCard) return '-';
    return idCard.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2');
  },
  
  // 计算订单状态统计
  getOrderStats() {
    return {
      pending: orders.filter(o => o.status === 'pending').length,
      dispatched: orders.filter(o => o.status === 'dispatched').length,
      inTransit: orders.filter(o => o.status === 'in_transit').length,
      arrived: orders.filter(o => o.status === 'arrived').length,
      completed: orders.filter(o => o.status === 'completed').length,
      cancelled: orders.filter(o => o.status === 'cancelled').length,
      exception: orders.filter(o => o.status === 'exception').length
    };
  },
  
  // 计算车辆状态统计
  getVehicleStats() {
    return {
      idle: vehicles.filter(v => v.status === 'idle').length,
      transporting: vehicles.filter(v => v.status === 'transporting').length,
      maintaining: vehicles.filter(v => v.status === 'maintaining').length,
      offline: vehicles.filter(v => v.status === 'offline').length
    };
  },
  
  // 计算司机状态统计
  getDriverStats() {
    return {
      idle: drivers.filter(d => d.status === 'idle').length,
      transporting: drivers.filter(d => d.status === 'transporting').length,
      onLeave: drivers.filter(d => d.status === 'onLeave').length
    };
  },
  
  // 计算异常状态统计
  getExceptionStats() {
    return {
      pending: exceptions.filter(e => e.status === 'pending').length,
      processing: exceptions.filter(e => e.status === 'processing').length,
      resolved: exceptions.filter(e => e.status === 'resolved').length
    };
  }
};