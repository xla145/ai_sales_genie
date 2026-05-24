/**
 * 智能物流系统 - Mock 数据
 * 用于原型演示，包含所有业务数据模拟
 */

// ==================== 全局配置 ====================
const MockConfig = {
  // 订单状态枚举
  orderStatus: {
    PENDING: { name: '待派单', color: '#fa8c16' },
    ASSIGNED: { name: '已派单', color: '#1890ff' },
    IN_TRANSPORT: { name: '运输中', color: '#1890ff' },
    ARRIVED: { name: '已到达', color: '#13c2c2' },
    SIGNED: { name: '已签收', color: '#52c41a' },
    COMPLETED: { name: '已完成', color: '#52c41a' },
    CANCELLED: { name: '已取消', color: '#8c8c8c' }
  },
  // 车辆状态枚举
  vehicleStatus: {
    IDLE: { name: '空闲', color: '#13c2c2' },
    IN_USE: { name: '使用中', color: '#1890ff' },
    MAINTENANCE: { name: '维修中', color: '#8c8c8c' },
    OFFLINE: { name: '离线', color: '#8c8c8c' }
  },
  // 司机状态枚举
  driverStatus: {
    IDLE: { name: '空闲', color: '#13c2c2' },
    WORKING: { name: '工作中', color: '#1890ff' },
    RESTING: { name: '休息中', color: '#8c8c8c' },
    OFF_DUTY: { name: '休息', color: '#8c8c8c' }
  },
  // 异常状态枚举
  exceptionStatus: {
    PENDING: { name: '待处理', color: '#fa8c16' },
    PROCESSING: { name: '处理中', color: '#1890ff' },
    RESOLVED: { name: '已解决', color: '#52c41a' },
    ESCALATED: { name: '已升级', color: '#ff4d4f' },
    CLOSED: { name: '已关闭', color: '#8c8c8c' }
  },
  // 异常类型枚举
  exceptionType: {
    DELAY: { name: '运输延迟', severity: 'medium' },
    DAMAGE: { name: '货物损坏', severity: 'high' },
    ACCIDENT: { name: '交通事故', severity: 'high' },
    ROUTE_DEV: { name: '路线偏离', severity: 'medium' },
    VEHICLE_FAIL: { name: '车辆故障', severity: 'medium' },
    WEATHER: { name: '天气异常', severity: 'low' },
    OTHER: { name: '其他异常', severity: 'low' }
  },
  // 货物类型枚举
  goodsType: {
    NORMAL: '普通货物',
    FRAGILE: '易碎品',
    FLAMMABLE: '易燃品',
    FRESH: '生鲜食品',
    ELECTRONIC: '电子产品',
    VALUABLE: '贵重物品',
    OTHER: '其他'
  },
  // 车型枚举
  vehicleType: {
    VAN: '厢式货车',
    FLATBED: '平板车',
    TANKER: '罐车',
    REFRIGERATED: '冷藏车',
    OTHER: '其他'
  },
  // 准驾车型枚举
  licenseType: ['A1', 'A2', 'A3', 'B1', 'B2', 'C1', 'C2']
};

// ==================== 用户与角色数据 ====================
const users = [
  { id: 'U001', username: 'admin', name: '系统管理员', role: '系统管理员', department: '总部', phone: '13800000001', email: 'admin@logistics.com' },
  { id: 'U002', username: 'manager', name: '张管理层', role: '管理人员', department: '运营部', phone: '13800000002', email: 'manager@logistics.com' },
  { id: 'U003', username: 'dispatcher', name: '李调度', role: '调度员', department: '调度部', phone: '13800000003', email: 'dispatcher@logistics.com' },
  { id: 'U004', username: 'operator', name: '王运营', role: '运营人员', department: '运营部', phone: '13800000004', email: 'operator@logistics.com' },
  { id: 'U005', username: 'driver1', name: '赵师傅', role: '司机', department: '运输部', phone: '13800000005', email: 'driver1@logistics.com' },
  { id: 'U006', username: 'vehicle_mgr', name: '钱车辆', role: '车辆管理人员', department: '后勤部', phone: '13800000006', email: 'vehicle_mgr@logistics.com' }
];

const roles = [
  { id: 'R001', name: '系统管理员', permissions: ['all'] },
  { id: 'R002', name: '管理人员', permissions: ['order:view', 'order:export', 'vehicle:view', 'driver:view', 'dispatch:view', 'track:view', 'exception:view', 'exception:approve', 'data:view', 'data:export'] },
  { id: 'R003', name: '调度员', permissions: ['order:view', 'order:dispatch', 'vehicle:view', 'driver:view', 'dispatch:operate', 'track:view', 'track:export', 'exception:view', 'exception:handle'] },
  { id: 'R004', name: '运营人员', permissions: ['order:view', 'order:create', 'order:edit', 'order:cancel', 'order:import', 'order:export', 'track:view'] },
  { id: 'R005', name: '司机', permissions: ['task:view', 'task:accept', 'track:view', 'track:report', 'exception:report'] },
  { id: 'R006', name: '车辆管理人员', permissions: ['vehicle:view', 'vehicle:create', 'vehicle:edit', 'vehicle:delete', 'track:view'] }
];

// ==================== 首页数据 ====================
const homeData = {
  // 今日概览
  overview: {
    todayOrderCount: 128,
    inTransportCount: 45,
    exceptionCount: 3,
    todayIncome: 126800
  },
  // 待办事项
  todoList: [
    { id: 'T001', type: 'pending_dispatch', title: '待派单订单', count: 5, priority: 'high', path: '/dispatch/center' },
    { id: 'T002', type: 'pending_exception', title: '待处理异常', count: 3, priority: 'high', path: '/exception/list' },
    { id: 'T003', type: 'pending_sign', title: '待签收订单', count: 2, priority: 'medium', path: '/order/list?status=SIGNED' },
    { id: 'T004', type: 'pending_audit', title: '待审批调度', count: 1, priority: 'medium', path: '/dispatch/audit' }
  ],
  // 快捷入口
  quickEntry: [
    { name: '新建订单', icon: 'plus', path: '/order/create', roles: ['运营人员', '调度员', '管理人员', '系统管理员'] },
    { name: '车辆管理', icon: 'truck', path: '/vehicle/list', roles: ['调度员', '车辆管理人员', '管理人员', '系统管理员'] },
    { name: '调度中心', icon: 'location', path: '/dispatch/center', roles: ['调度员', '管理人员', '系统管理员'] },
    { name: '运输轨迹', icon: 'map', path: '/transport/track', roles: ['所有'] },
    { name: '异常处理', icon: 'warning', path: '/exception/list', roles: ['调度员', '管理人员', '系统管理员'] },
    { name: '数据看板', icon: 'chart', path: '/data/board', roles: ['管理人员', '系统管理员'] }
  ],
  // 趋势数据（近7天）
  trendData: {
    days7: [
      { date: '01-09', orderCount: 98, income: 98000 },
      { date: '01-10', orderCount: 112, income: 112000 },
      { date: '01-11', orderCount: 105, income: 105000 },
      { date: '01-12', orderCount: 125, income: 125000 },
      { date: '01-13', orderCount: 118, income: 118000 },
      { date: '01-14', orderCount: 132, income: 132000 },
      { date: '01-15', orderCount: 128, income: 126800 }
    ],
    days30: [
      { date: '12-17', orderCount: 85, income: 85000 },
      { date: '12-18', orderCount: 92, income: 92000 },
      { date: '12-19', orderCount: 88, income: 88000 },
      { date: '12-20', orderCount: 105, income: 105000 },
      { date: '12-21', orderCount: 98, income: 98000 },
      { date: '12-22', orderCount: 115, income: 115000 },
      { date: '12-23', orderCount: 120, income: 120000 },
      { date: '12-24', orderCount: 108, income: 108000 },
      { date: '12-25', orderCount: 95, income: 95000 },
      { date: '12-26', orderCount: 102, income: 102000 },
      { date: '12-27', orderCount: 110, income: 110000 },
      { date: '12-28', orderCount: 118, income: 118000 },
      { date: '12-29', orderCount: 125, income: 125000 },
      { date: '12-30', orderCount: 130, income: 130000 },
      { date: '12-31', orderCount: 135, income: 135000 },
      { date: '01-01', orderCount: 78, income: 78000 },
      { date: '01-02', orderCount: 85, income: 85000 },
      { date: '01-03', orderCount: 92, income: 92000 },
      { date: '01-04', orderCount: 100, income: 100000 },
      { date: '01-05', orderCount: 108, income: 108000 },
      { date: '01-06', orderCount: 115, income: 115000 },
      { date: '01-07', orderCount: 98, income: 98000 },
      { date: '01-08', orderCount: 105, income: 105000 },
      { date: '01-09', orderCount: 98, income: 98000 },
      { date: '01-10', orderCount: 112, income: 112000 },
      { date: '01-11', orderCount: 105, income: 105000 },
      { date: '01-12', orderCount: 125, income: 125000 },
      { date: '01-13', orderCount: 118, income: 118000 },
      { date: '01-14', orderCount: 132, income: 132000 },
      { date: '01-15', orderCount: 128, income: 126800 }
    ]
  }
};

// ==================== 订单数据 ====================
const orders = [
  {
    id: 'ORD001', orderNo: 'LOG202401150001', status: 'IN_TRANSPORT',
    customerName: '北京科技有限公司', customerPhone: '13800138001',
    shipperName: '张三', shipperPhone: '13900139001',
    shipperAddress: '北京市朝阳区光华路10号物流园A区',
    consigneeName: '李四', consigneePhone: '13900139002',
    consigneeAddress: '天津市滨海新区港城大道88号',
    goodsName: '电子产品', goodsType: 'ELECTRONIC', goodsWeight: 500, goodsVolume: 5,
    goodsQuantity: 20, goodsValue: 100000, packagingType: '纸箱',
    expectedDeliveryTime: '2024-01-15 18:00:00',
    freightFee: 800, loadingFee: 100, insuranceFee: 50, otherFee: 0, totalFee: 950,
    paymentStatus: 'PAID', paymentTime: '2024-01-15 09:35:00',
    createTime: '2024-01-15 09:30:00', updateTime: '2024-01-15 10:30:00',
    assignedVehicle: '京A12345', assignedDriver: '王师傅'
  },
  {
    id: 'ORD002', orderNo: 'LOG202401150002', status: 'PENDING',
    customerName: '上海贸易公司', customerPhone: '13800138002',
    shipperName: '赵六', shipperPhone: '13900139003',
    shipperAddress: '上海市浦东新区张江高科技园区',
    consigneeName: '钱七', consigneePhone: '13900139004',
    consigneeAddress: '广州市天河区珠江新城',
    goodsName: '办公家具', goodsType: 'NORMAL', goodsWeight: 2000, goodsVolume: 15,
    goodsQuantity: 50, goodsValue: 50000, packagingType: '木箱',
    expectedDeliveryTime: '2024-01-16 18:00:00',
    freightFee: 1500, loadingFee: 200, insuranceFee: 100, otherFee: 0, totalFee: 1800,
    paymentStatus: 'PAID', paymentTime: '2024-01-15 10:00:00',
    createTime: '2024-01-15 09:45:00', updateTime: '2024-01-15 09:45:00',
    assignedVehicle: null, assignedDriver: null
  },
  {
    id: 'ORD003', orderNo: 'LOG202401150003', status: 'ASSIGNED',
    customerName: '深圳电子厂', customerPhone: '13800138003',
    shipperName: '孙八', shipperPhone: '13900139005',
    shipperAddress: '深圳市宝安区石岩街道',
    consigneeName: '周九', consigneePhone: '13900139006',
    consigneeAddress: '东莞市南城区宏远路',
    goodsName: '电子元器件', goodsType: 'ELECTRONIC', goodsWeight: 300, goodsVolume: 2,
    goodsQuantity: 100, goodsValue: 200000, packagingType: '防静电箱',
    expectedDeliveryTime: '2024-01-15 16:00:00',
    freightFee: 600, loadingFee: 80, insuranceFee: 80, otherFee: 0, totalFee: 760,
    paymentStatus: 'PAID', paymentTime: '2024-01-15 10:15:00',
    createTime: '2024-01-15 10:10:00', updateTime: '2024-01-15 10:25:00',
    assignedVehicle: '京B67890', assignedDriver: '李师傅'
  },
  {
    id: 'ORD004', orderNo: 'LOG202401150004', status: 'ARRIVED',
    customerName: '广州服装城', customerPhone: '13800138004',
    shipperName: '吴十', shipperPhone: '13900139007',
    shipperAddress: '广州市海珠区中大布匹市场',
    consigneeName: '郑一', consigneePhone: '13900139008',
    consigneeAddress: '杭州市四季青服装批发市场',
    goodsName: '服装面料', goodsType: 'NORMAL', goodsWeight: 1500, goodsVolume: 20,
    goodsQuantity: 30, goodsValue: 80000, packagingType: '编织袋',
    expectedDeliveryTime: '2024-01-15 14:00:00',
    freightFee: 1200, loadingFee: 150, insuranceFee: 60, otherFee: 0, totalFee: 1410,
    paymentStatus: 'PAID', paymentTime: '2024-01-15 08:30:00',
    createTime: '2024-01-15 08:20:00', updateTime: '2024-01-15 13:45:00',
    assignedVehicle: '京C11111', assignedDriver: '张师傅'
  },
  {
    id: 'ORD005', orderNo: 'LOG202401150005', status: 'SIGNED',
    customerName: '成都食品公司', customerPhone: '13800138005',
    shipperName: '陈二', shipperPhone: '13900139009',
    shipperAddress: '成都市金牛区荷花池市场',
    consigneeName: '林三', consigneePhone: '13900139010',
    consigneeAddress: '重庆市渝中区解放碑商圈',
    goodsName: '休闲食品', goodsType: 'FRESH', goodsWeight: 800, goodsVolume: 10,
    goodsQuantity: 200, goodsValue: 40000, packagingType: '纸箱',
    expectedDeliveryTime: '2024-01-15 12:00:00',
    freightFee: 1000, loadingFee: 120, insuranceFee: 40, otherFee: 0, totalFee: 1160,
    paymentStatus: 'PAID', paymentTime: '2024-01-15 07:45:00',
    createTime: '2024-01-15 07:30:00', updateTime: '2024-01-15 11:30:00',
    signedTime: '2024-01-15 11:25:00', signedBy: '林三', signedRemark: '货物完好',
    assignedVehicle: '京D22222', assignedDriver: '刘师傅'
  },
  {
    id: 'ORD006', orderNo: 'LOG202401150006', status: 'COMPLETED',
    customerName: '武汉建材市场', customerPhone: '13800138006',
    shipperName: '黄四', shipperPhone: '13900139011',
    shipperAddress: '武汉市硚口区汉正街建材市场',
    consigneeName: '徐五', consigneePhone: '13900139012',
    consigneeAddress: '长沙市雨花区高桥建材市场',
    goodsName: '建筑材料', goodsType: 'NORMAL', goodsWeight: 5000, goodsVolume: 30,
    goodsQuantity: 10, goodsValue: 30000, packagingType: '托盘',
    expectedDeliveryTime: '2024-01-14 18:00:00',
    freightFee: 2000, loadingFee: 300, insuranceFee: 30, otherFee: 0, totalFee: 2330,
    paymentStatus: 'PAID', paymentTime: '2024-01-14 09:00:00',
    createTime: '2024-01-14 08:50:00', updateTime: '2024-01-14 17:30:00',
    signedTime: '2024-01-14 17:20:00', signedBy: '徐五', signedRemark: '已验收',
    assignedVehicle: '京E33333', assignedDriver: '周师傅'
  },
  {
    id: 'ORD007', orderNo: 'LOG202401150007', status: 'CANCELLED',
    customerName: '南京化工公司', customerPhone: '13800138007',
    shipperName: '许六', shipperPhone: '13900139013',
    shipperAddress: '南京市栖霞区化工园区',
    consigneeName: '何七', consigneePhone: '13900139014',
    consigneeAddress: '苏州市工业园区',
    goodsName: '化工原料', goodsType: 'FLAMMABLE', goodsWeight: 1000, goodsVolume: 8,
    goodsQuantity: 20, goodsValue: 60000, packagingType: '专用罐',
    expectedDeliveryTime: '2024-01-16 10:00:00',
    freightFee: 900, loadingFee: 100, insuranceFee: 150, otherFee: 0, totalFee: 1150,
    paymentStatus: 'REFUNDED', paymentTime: '2024-01-15 11:00:00',
    createTime: '2024-01-15 10:50:00', updateTime: '2024-01-15 14:30:00',
    cancelReason: '客户要求取消订单', cancelTime: '2024-01-15 14:30:00',
    assignedVehicle: null, assignedDriver: null
  },
  {
    id: 'ORD008', orderNo: 'LOG202401150008', status: 'PENDING',
    customerName: '西安商贸公司', customerPhone: '13800138008',
    shipperName: '冯八', shipperPhone: '13900139015',
    shipperAddress: '西安市莲湖区土门商圈',
    consigneeName: '宋九', consigneePhone: '13900139016',
    consigneeAddress: '兰州市城关区东方红广场',
    goodsName: '日用百货', goodsType: 'NORMAL', goodsWeight: 600, goodsVolume: 12,
    goodsQuantity: 80, goodsValue: 25000, packagingType: '纸箱',
    expectedDeliveryTime: '2024-01-17 18:00:00',
    freightFee: 1100, loadingFee: 100, insuranceFee: 30, otherFee: 0, totalFee: 1230,
    paymentStatus: 'PAID', paymentTime: '2024-01-15 14:00:00',
    createTime: '2024-01-15 13:50:00', updateTime: '2024-01-15 13:50:00',
    assignedVehicle: null, assignedDriver: null
  },
  {
    id: 'ORD009', orderNo: 'LOG202401150009', status: 'PENDING',
    customerName: '天津制造厂', customerPhone: '13800138009',
    shipperName: '韩十', shipperPhone: '13900139017',
    shipperAddress: '天津市东丽区工业园',
    consigneeName: '唐一', consigneePhone: '13900139018',
    consigneeAddress: '青岛市黄岛区海尔工业园',
    goodsName: '机械设备', goodsType: 'VALUABLE', goodsWeight: 3000, goodsVolume: 25,
    goodsQuantity: 5, goodsValue: 500000, packagingType: '木箱+托盘',
    expectedDeliveryTime: '2024-01-18 12:00:00',
    freightFee: 2500, loadingFee: 400, insuranceFee: 500, otherFee: 0, totalFee: 3400,
    paymentStatus: 'PAID', paymentTime: '2024-01-15 15:30:00',
    createTime: '2024-01-15 15:20:00', updateTime: '2024-01-15 15:20:00',
    assignedVehicle: null, assignedDriver: null
  },
  {
    id: 'ORD010', orderNo: 'LOG202401150010', status: 'PENDING',
    customerName: '沈阳医药公司', customerPhone: '13800138010',
    shipperName: '周二', shipperPhone: '13900139019',
    shipperAddress: '沈阳市铁西区经济技术开发区',
    consigneeName: '姜三', consigneePhone: '13900139020',
    consigneeAddress: '大连市甘井子区医药产业园',
    goodsName: '药品', goodsType: 'FRAGILE', goodsWeight: 200, goodsVolume: 3,
    goodsQuantity: 50, goodsValue: 300000, packagingType: '冷藏箱',
    expectedDeliveryTime: '2024-01-16 08:00:00',
    freightFee: 700, loadingFee: 80, insuranceFee: 300, otherFee: 0, totalFee: 1080,
    paymentStatus: 'PAID', paymentTime: '2024-01-15 16:00:00',
    createTime: '2024-01-15 15:50:00', updateTime: '2024-01-15 15:50:00',
    assignedVehicle: null, assignedDriver: null
  },
  // 更多订单数据以满足演示需求
  {
    id: 'ORD011', orderNo: 'LOG202401150011', status: 'IN_TRANSPORT',
    customerName: '郑州物流园', customerPhone: '13800138011',
    shipperName: '谭四', shipperPhone: '13900139021',
    shipperAddress: '郑州市经开区物流园区',
    consigneeName: '袁五', consigneePhone: '13900139022',
    consigneeAddress: '太原市小店区',
    goodsName: '快递包裹', goodsType: 'NORMAL', goodsWeight: 150, goodsVolume: 3,
    goodsQuantity: 30, goodsValue: 15000, packagingType: '纸箱',
    expectedDeliveryTime: '2024-01-15 20:00:00',
    freightFee: 400, loadingFee: 50, insuranceFee: 20, otherFee: 0, totalFee: 470,
    paymentStatus: 'PAID', paymentTime: '2024-01-15 17:00:00',
    createTime: '2024-01-15 16:45:00', updateTime: '2024-01-15 17:30:00',
    assignedVehicle: '京F44444', assignedDriver: '郑师傅'
  },
  {
    id: 'ORD012', orderNo: 'LOG202401150012', status: 'IN_TRANSPORT',
    customerName: '哈尔滨商场', customerPhone: '13800138012',
    shipperName: '卢六', shipperPhone: '13900139023',
    shipperAddress: '哈尔滨市南岗区中央大街',
    consigneeName: '秦七', consigneePhone: '13900139024',
    consigneeAddress: '长春市朝阳区',
    goodsName: '冬季服装', goodsType: 'NORMAL', goodsWeight: 400, goodsVolume: 8,
    goodsQuantity: 60, goodsValue: 80000, packagingType: '纸箱',
    expectedDeliveryTime: '2024-01-15 22:00:00',
    freightFee: 800, loadingFee: 80, insuranceFee: 80, otherFee: 0, totalFee: 960,
    paymentStatus: 'PAID', paymentTime: '2024-01-15 17:30:00',
    createTime: '2024-01-15 17:20:00', updateTime: '2024-01-15 18:00:00',
    assignedVehicle: '京G55555', assignedDriver: '齐师傅'
  }
];

// ==================== 车辆数据 ====================
const vehicles = [
  { id: 'V001', plateNumber: '京A12345', vehicleType: 'VAN', loadCapacity: 10, company: '北京物流公司', status: 'IN_USE', driverName: '王师傅', driverPhone: '13700137001', phone: '010-12345601', location: '北京市通州区', insuranceExpiry: '2024-06-30', maintenanceDate: '2024-01-05', nextMaintenanceDate: '2024-04-05', createTime: '2023-01-01 10:00:00', updateTime: '2024-01-15 14:20:00' },
  { id: 'V002', plateNumber: '京B67890', vehicleType: 'REFRIGERATED', loadCapacity: 8, company: '北京物流公司', status: 'IN_USE', driverName: '李师傅', driverPhone: '13700137002', phone: '010-12345602', location: '北京市大兴区', insuranceExpiry: '2024-07-15', maintenanceDate: '2024-01-10', nextMaintenanceDate: '2024-04-10', createTime: '2023-02-15 10:00:00', updateTime: '2024-01-15 14:18:00' },
  { id: 'V003', plateNumber: '京C11111', vehicleType: 'FLATBED', loadCapacity: 15, company: '北京物流公司', status: 'IDLE', driverName: null, driverPhone: null, phone: '010-12345603', location: '北京市朝阳区', insuranceExpiry: '2024-08-01', maintenanceDate: '2023-12-20', nextMaintenanceDate: '2024-03-20', createTime: '2023-03-01 10:00:00', updateTime: '2024-01-15 12:00:00' },
  { id: 'V004', plateNumber: '京D22222', vehicleType: 'VAN', loadCapacity: 12, company: '北京物流公司', status: 'IDLE', driverName: null, driverPhone: null, phone: '010-12345604', location: '北京市海淀区', insuranceExpiry: '2024-09-01', maintenanceDate: '2024-01-01', nextMaintenanceDate: '2024-04-01', createTime: '2023-04-10 10:00:00', updateTime: '2024-01-15 10:00:00' },
  { id: 'V005', plateNumber: '京E33333', vehicleType: 'TANKER', loadCapacity: 20, company: '北京物流公司', status: 'IDLE', driverName: null, driverPhone: null, phone: '010-12345605', location: '北京市丰台区', insuranceExpiry: '2024-05-20', maintenanceDate: '2023-11-15', nextMaintenanceDate: '2024-02-15', createTime: '2023-05-20 10:00:00', updateTime: '2024-01-14 18:00:00' },
  { id: 'V006', plateNumber: '京F44444', vehicleType: 'VAN', loadCapacity: 10, company: '北京物流公司', status: 'IN_USE', driverName: '郑师傅', driverPhone: '13700137006', phone: '010-12345606', location: '天津市武清区', insuranceExpiry: '2024-06-15', maintenanceDate: '2024-01-08', nextMaintenanceDate: '2024-04-08', createTime: '2023-06-01 10:00:00', updateTime: '2024-01-15 17:30:00' },
  { id: 'V007', plateNumber: '京G55555', vehicleType: 'VAN', loadCapacity: 10, company: '北京物流公司', status: 'IN_USE', driverName: '齐师傅', driverPhone: '13700137007', phone: '010-12345607', location: '河北省廊坊市', insuranceExpiry: '2024-07-01', maintenanceDate: '2023-12-25', nextMaintenanceDate: '2024-03-25', createTime: '2023-07-10 10:00:00', updateTime: '2024-01-15 18:00:00' },
  { id: 'V008', plateNumber: '京H66666', vehicleType: 'FLATBED', loadCapacity: 18, company: '北京物流公司', status: 'MAINTENANCE', driverName: null, driverPhone: null, phone: '010-12345608', location: '北京市顺义区维修厂', insuranceExpiry: '2024-08-15', maintenanceDate: '2024-01-15', nextMaintenanceDate: '2024-01-20', createTime: '2023-08-15 10:00:00', updateTime: '2024-01-15 09:00:00' },
  { id: 'V009', plateNumber: '京J77777', vehicleType: 'REFRIGERATED', loadCapacity: 6, company: '北京物流公司', status: 'IDLE', driverName: null, driverPhone: null, phone: '010-12345609', location: '北京市昌平区', insuranceExpiry: '2024-09-20', maintenanceDate: '2024-01-02', nextMaintenanceDate: '2024-04-02', createTime: '2023-09-01 10:00:00', updateTime: '2024-01-15 08:00:00' },
  { id: 'V010', plateNumber: '京K88888', vehicleType: 'VAN', loadCapacity: 8, company: '北京物流公司', status: 'OFFLINE', driverName: '孙师傅', driverPhone: '13700137010', phone: '010-12345610', location: '未知', insuranceExpiry: '2024-10-01', maintenanceDate: '2023-10-10', nextMaintenanceDate: '2024-01-10', createTime: '2023-10-15 10:00:00', updateTime: '2024-01-14 20:00:00' },
  { id: 'V011', plateNumber: '津A11111', vehicleType: 'VAN', loadCapacity: 10, company: '天津物流公司', status: 'IDLE', driverName: null, driverPhone: null, phone: '022-12345601', location: '天津市东丽区', insuranceExpiry: '2024-06-01', maintenanceDate: '2023-12-01', nextMaintenanceDate: '2024-03-01', createTime: '2023-11-01 10:00:00', updateTime: '2024-01-15 07:00:00' },
  { id: 'V012', plateNumber: '津B22222', vehicleType: 'FLATBED', loadCapacity: 15, company: '天津物流公司', status: 'IDLE', driverName: null, driverPhone: null, phone: '022-12345602', location: '天津市西青区', insuranceExpiry: '2024-07-10', maintenanceDate: '2024-01-05', nextMaintenanceDate: '2024-04-05', createTime: '2023-12-10 10:00:00', updateTime: '2024-01-15 06:00:00' }
];

// ==================== 司机数据 ====================
const drivers = [
  { id: 'D001', name: '王师傅', phone: '13700137001', idCard: '110101198001011234', drivingLicense: 'A2', licenseExpiry: '2026-05-15', company: '北京物流公司', department: '运输部', status: 'WORKING', totalOrders: 1250, totalMileage: 185000, rating: 4.8, createTime: '2020-01-01 10:00:00', updateTime: '2024-01-15 14:20:00' },
  { id: 'D002', name: '李师傅', phone: '13700137002', idCard: '110101198102021235', drivingLicense: 'A1', licenseExpiry: '2025-08-20', company: '北京物流公司', department: '运输部', status: 'WORKING', totalOrders: 980, totalMileage: 142000, rating: 4.9, createTime: '2020-02-15 10:00:00', updateTime: '2024-01-15 14:18:00' },
  { id: 'D003', name: '张师傅', phone: '13700137003', idCard: '110101198203031236', drivingLicense: 'B2', licenseExpiry: '2025-11-10', company: '北京物流公司', department: '运输部', status: 'IDLE', totalOrders: 756, totalMileage: 98000, rating: 4.7, createTime: '2020-03-01 10:00:00', updateTime: '2024-01-15 13:45:00' },
  { id: 'D004', name: '刘师傅', phone: '13700137004', idCard: '110101198304041237', drivingLicense: 'A2', licenseExpiry: '2026-02-28', company: '北京物流公司', department: '运输部', status: 'WORKING', totalOrders: 1100, totalMileage: 165000, rating: 4.85, createTime: '2020-04-10 10:00:00', updateTime: '2024-01-15 11:30:00' },
  { id: 'D005', name: '赵师傅', phone: '13700137005', idCard: '110101198405051238', drivingLicense: 'B1', licenseExpiry: '2025-06-15', company: '北京物流公司', department: '运输部', status: 'IDLE', totalOrders: 650, totalMileage: 85000, rating: 4.6, createTime: '2020-05-20 10:00:00', updateTime: '2024-01-14 18:00:00' },
  { id: 'D006', name: '郑师傅', phone: '13700137006', idCard: '110101198506061239', drivingLicense: 'A2', licenseExpiry: '2026-09-01', company: '北京物流公司', department: '运输部', status: 'WORKING', totalOrders: 890, totalMileage: 128000, rating: 4.75, createTime: '2020-06-01 10:00:00', updateTime: '2024-01-15 17:30:00' },
  { id: 'D007', name: '齐师傅', phone: '13700137007', idCard: '110101198607071240', drivingLicense: 'A1', licenseExpiry: '2025-12-20', company: '北京物流公司', department: '运输部', status: 'WORKING', totalOrders: 1020, totalMileage: 152000, rating: 4.8, createTime: '2020-07-10 10:00:00', updateTime: '2024-01-15 18:00:00' },
  { id: 'D008', name: '周师傅', phone: '13700137008', idCard: '110101198708081241', drivingLicense: 'B2', licenseExpiry: '2026-03-10', company: '北京物流公司', department: '运输部', status: 'RESTING', totalOrders: 540, totalMileage: 72000, rating: 4.65, createTime: '2020-08-15 10:00:00', updateTime: '2024-01-15 12:00:00' },
  { id: 'D009', name: '吴师傅', phone: '13700137009', idCard: '110101198809091242', drivingLicense: 'A2', licenseExpiry: '2025-07-25', company: '北京物流公司', department: '运输部', status: 'IDLE', totalOrders: 780, totalMileage: 105000, rating: 4.7, createTime: '2020-09-01 10:00:00', updateTime: '2024-01-15 10:00:00' },
  { id: 'D010', name: '孙师傅', phone: '13700137010', idCard: '110101198910101243', drivingLicense: 'B1', licenseExpiry: '2026-01-30', company: '北京物流公司', department: '运输部', status: 'OFF_DUTY', totalOrders: 420, totalMileage: 56000, rating: 4.55, createTime: '2020-10-15 10:00:00', updateTime: '2024-01-14 20:00:00' }
];

// ==================== 异常数据 ====================
const exceptions = [
  { id: 'EX001', orderId: 'ORD001', orderNo: 'LOG202401150001', type: 'DELAY', status: 'PROCESSING', description: '因京津冀地区大雾天气，高速公路临时封闭，车辆预计延迟2小时到达', reportTime: '2024-01-15 11:00:00', reportBy: '王师傅', handleTime: null, handleBy: null, handleResult: null, severity: 'medium', createTime: '2024-01-15 11:00:00', updateTime: '2024-01-15 11:30:00' },
  { id: 'EX002', orderId: 'ORD003', orderNo: 'LOG202401150003', type: 'ROUTE_DEV', status: 'PENDING', description: '车辆偏离规划路线超过5公里，系统自动检测到异常', reportTime: '2024-01-15 10:45:00', reportBy: '系统', handleTime: null, handleBy: null, handleResult: null, severity: 'medium', createTime: '2024-01-15 10:45:00', updateTime: '2024-01-15 10:45:00' },
  { id: 'EX003', orderId: 'ORD011', orderNo: 'LOG202401150011', type: 'VEHICLE_FAIL', status: 'PENDING', description: '车辆在运输途中出现轻微故障，已临时停靠路边检查', reportTime: '2024-01-15 16:30:00', reportBy: '郑师傅', handleTime: null, handleBy: null, handleResult: null, severity: 'medium', createTime: '2024-01-15 16:30:00', updateTime: '2024-01-15 16:30:00' },
  { id: 'EX004', orderId: 'ORD006', orderNo: 'LOG202401150006', type: 'DAMAGE', status: 'RESOLVED', description: '货物在运输过程中因颠簸导致部分包装破损，已重新加固', reportTime: '2024-01-14 14:00:00', reportBy: '张师傅', handleTime: '2024-01-14 16:30:00', handleBy: '李调度', handleResult: '已对货物进行重新加固，客户确认无异议，订单继续执行', severity: 'high', createTime: '2024-01-14 14:00:00', updateTime: '2024-01-14 16:30:00' },
  { id: 'EX005', orderId: 'ORD004', orderNo: 'LOG202401150004', type: 'WEATHER', status: 'CLOSED', description: '因大雾天气影响，高速公路拥堵，到达时间延迟', reportTime: '2024-01-15 08:30:00', reportBy: '系统', handleTime: '2024-01-15 13:40:00', handleBy: '张管理层', handleResult: '天气好转，道路恢复通行，货物已安全送达', severity: 'low', createTime: '2024-01-15 08:30:00', updateTime: '2024-01-15 13:45:00' }
];

// ==================== 轨迹数据 ====================
const trackPoints = [
  // 订单ORD001的轨迹
  { orderId: 'ORD001', vehicleId: 'V001', points: [
    { time: '2024-01-15 10:30:00', lat: 39.9042, lng: 116.4074, speed: 45, direction: '东', address: '北京市朝阳区光华路10号', isAnomaly: false },
    { time: '2024-01-15 10:45:00', lat: 39.9142, lng: 116.4174, speed: 52, direction: '东', address: '北京市朝阳区建国路', isAnomaly: false },
    { time: '2024-01-15 11:00:00', lat: 39.9242, lng: 116.4274, speed: 48, direction: '东', address: '北京市通州区运河西大街', isAnomaly: false },
    { time: '2024-01-15 11:15:00', lat: 39.9342, lng: 116.4374, speed: 55, direction: '东', address: '北京市通州区京塘路', isAnomaly: false },
    { time: '2024-01-15 11:30:00', lat: 39.9442, lng: 116.4474, speed: 0, direction: '东', address: '天津市武清区', isAnomaly: true, anomalyReason: '长时间停留' },
    { time: '2024-01-15 11:45:00', lat: 39.9442, lng: 116.4474, speed: 50, direction: '东', address: '天津市武清区', isAnomaly: false },
    { time: '2024-01-15 12:00:00', lat: 39.1542, lng: 117.2074, speed: 58, direction: '东南', address: '天津市静海区', isAnomaly: false },
    { time: '2024-01-15 12:15:00', lat: 39.0542, lng: 117.3074, speed: 52, direction: '南', address: '天津市滨海新区', isAnomaly: false },
    { time: '2024-01-15 12:30:00', lat: 39.0042, lng: 117.4074, speed: 45, direction: '南', address: '天津市滨海新区港城大道', isAnomaly: false }
  ]},
  // 订单ORD003的轨迹
  { orderId: 'ORD003', vehicleId: 'V002', points: [
    { time: '2024-01-15 10:25:00', lat: 22.5431, lng: 114.0549, speed: 40, direction: '北', address: '深圳市宝安区石岩街道', isAnomaly: false },
    { time: '2024-01-15 10:40:00', lat: 22.5531, lng: 114.0649, speed: 55, direction: '北', address: '深圳市龙华区', isAnomaly: false },
    { time: '2024-01-15 10:55:00', lat: 22.5631, lng: 114.0749, speed: 48, direction: '东北', address: '东莞市大朗镇', isAnomaly: false },
    { time: '2024-01-15 11:10:00', lat: 22.5731, lng: 114.0149, speed: 52, direction: '西北', address: '东莞市大岭山镇', isAnomaly: false, anomalyReason: '路线偏离' },
    { time: '2024-01-15 11:25:00', lat: 22.5831, lng: 113.7549, speed: 45, direction: '西', address: '东莞市南城区', isAnomaly: false }
  ]}
];

// ==================== 统计数据 ====================
const statisticsData = {
  // 订单统计
  orderStats: {
    total: 4528,
    today: 128,
    pending: 45,
    inTransport: 156,
    completed: 4280,
    cancelled: 95,
    completionRate: 94.5,
    trend: [98, 112, 105, 125, 118, 132, 128]
  },
  // 运输统计
  transportStats: {
    totalMileage: 1256800,
    todayMileage: 8560,
    avgMileagePerDay: 12500,
    avgDeliveryTime: 4.5,
    onTimeRate: 92.3,
    trend: [8200, 9100, 8600, 9800, 8900, 10200, 8560]
  },
  // 收入统计
  incomeStats: {
    total: 5680000,
    today: 126800,
    month: 3865000,
    avgOrderValue: 1255,
    trend: [98000, 112000, 105000, 125000, 118000, 132000, 126800]
  },
  // 车辆统计
  vehicleStats: {
    total: 25,
    inUse: 12,
    idle: 8,
    maintenance: 3,
    offline: 2,
    utilizationRate: 48,
    avgMileagePerVehicle: 50272
  },
  // 司机统计
  driverStats: {
    total: 30,
    working: 12,
    idle: 10,
    resting: 5,
    offDuty: 3,
    avgOrdersPerDriver: 151,
    avgRating: 4.72
  },
  // 异常统计
  exceptionStats: {
    total: 156,
    pending: 3,
    processing: 5,
    resolved: 145,
    escalated: 3,
    types: [
      { name: '运输延迟', count: 45 },
      { name: '货物损坏', count: 12 },
      { name: '路线偏离', count: 28 },
      { name: '车辆故障', count: 35 },
      { name: '天气异常', count: 22 },
      { name: '其他', count: 14 }
    ]
  }
};

// ==================== 智能调度数据 ====================
const dispatchData = {
  // 待派单订单
  pendingOrders: orders.filter(o => o.status === 'PENDING'),
  // 可用车辆
  availableVehicles: vehicles.filter(v => v.status === 'IDLE'),
  // 可用司机
  availableDrivers: drivers.filter(d => d.status === 'IDLE'),
  // 派单推荐结果示例
  dispatchRecommendation: {
    orderId: 'ORD002',
    recommendedVehicle: { vehicleId: 'V003', plateNumber: '京C11111', vehicleType: 'FLATBED', loadCapacity: 15, matchScore: 95 },
    recommendedDriver: { driverId: 'D003', name: '张师傅', licenseType: 'B2', matchScore: 90 },
    route: {
      distance: 1450,
      duration: 960,
      points: [
        { address: '上海市浦东新区张江高科技园区', lat: 31.2069, lng: 121.6538 },
        { address: '途经点1', lat: 30.5742, lng: 120.2928 },
        { address: '广州市天河区珠江新城', lat: 23.1291, lng: 113.2644 }
      ]
    }
  }
};

// ==================== 系统设置数据 ====================
const systemSettings = {
  // 用户列表
  users: users,
  // 角色列表
  roles: roles,
  // 组织架构
  organizations: [
    { id: 'ORG001', name: '北京物流公司', parentId: null, level: 1, type: 'company' },
    { id: 'ORG002', name: '运营部', parentId: 'ORG001', level: 2, type: 'department' },
    { id: 'ORG003', name: '调度部', parentId: 'ORG001', level: 2, type: 'department' },
    { id: 'ORG004', name: '运输部', parentId: 'ORG001', level: 2, type: 'department' },
    { id: 'ORG005', name: '后勤部', parentId: 'ORG001', level: 2, type: 'department' },
    { id: 'ORG006', name: '天津物流公司', parentId: null, level: 1, type: 'company' }
  ],
  // 系统参数
  params: [
    { id: 'P001', paramKey: 'order.autoCancel.hours', paramName: '订单自动取消时长', paramValue: '24', paramType: 'number', paramDesc: '待派单订单超过此时间未派单自动取消' },
    { id: 'P002', paramKey: 'track.refresh.interval', paramName: '轨迹刷新间隔', paramValue: '30', paramType: 'number', paramDesc: '实时定位刷新间隔，单位秒' },
    { id: 'P003', paramKey: 'dispatch.auto.enable', paramName: '智能派单自动确认', paramValue: 'false', paramType: 'boolean', paramDesc: '智能派单是否自动确认' },
    { id: 'P004', paramKey: 'exception.escalate.hours', paramName: '异常升级时长', paramValue: '2', paramType: 'number', paramDesc: '异常超过此时间未处理自动升级' },
    { id: 'P005', paramKey: 'vehicle.maintenance.remind.days', paramName: '维保提前提醒天数', paramValue: '7', paramType: 'number', paramDesc: '维保到期前提醒天数' }
  ],
  // 操作日志
  logs: [
    { id: 'L001', operator: '王运营', operation: '创建订单', content: '创建订单LOG202401150012', ip: '192.168.1.100', time: '2024-01-15 17:20:00' },
    { id: 'L002', operator: '李调度', operation: '派单', content: '订单LOG202401150001派单给车辆京A12345、司机王师傅', ip: '192.168.1.101', time: '2024-01-15 10:25:00' },
    { id: 'L003', operator: '李调度', operation: '派单', content: '订单LOG202401150003派单给车辆京B67890、司机李师傅', ip: '192.168.1.101', time: '2024-01-15 10:24:00' },
    { id: 'L004', operator: '王师傅', operation: '开始运输', content: '订单LOG202401150001开始运输', ip: '192.168.1.200', time: '2024-01-15 10:30:00' },
    { id: 'L005', operator: '系统', operation: '异常预警', content: '订单LOG202401150003检测到路线偏离', ip: '127.0.0.1', time: '2024-01-15 11:10:00' }
  ]
};

// ==================== 导出数据对象 ====================
const MockData = {
  // 配置
  config: MockConfig,
  // 用户与角色
  users,
  roles,
  // 首页
  home: homeData,
  // 订单
  orders,
  // 车辆
  vehicles,
  // 司机
  drivers,
  // 异常
  exceptions,
  // 轨迹
  trackPoints,
  // 统计
  statistics: statisticsData,
  // 调度
  dispatch: dispatchData,
  // 系统设置
  system: systemSettings,

  // ==================== 工具方法 ====================
  // 获取订单列表
  getOrders: function(filters = {}) {
    let result = [...orders];
    if (filters.status && filters.status !== 'all') {
      result = result.filter(o => o.status === filters.status);
    }
    if (filters.keyword) {
      const kw = filters.keyword.toLowerCase();
      result = result.filter(o =>
        o.orderNo.toLowerCase().includes(kw) ||
        o.customerName.toLowerCase().includes(kw) ||
        o.shipperAddress.toLowerCase().includes(kw) ||
        o.consigneeAddress.toLowerCase().includes(kw)
      );
    }
    if (filters.dateRange && filters.dateRange.length === 2) {
      const [start, end] = filters.dateRange;
      result = result.filter(o => {
        const createTime = new Date(o.createTime);
        return createTime >= start && createTime <= end;
      });
    }
    return result;
  },

  // 获取订单详情
  getOrderById: function(orderId) {
    return orders.find(o => o.id === orderId || o.orderNo === orderId);
  },

  // 获取车辆列表
  getVehicles: function(filters = {}) {
    let result = [...vehicles];
    if (filters.status && filters.status !== 'all') {
      result = result.filter(v => v.status === filters.status);
    }
    if (filters.vehicleType && filters.vehicleType !== 'all') {
      result = result.filter(v => v.vehicleType === filters.vehicleType);
    }
    if (filters.keyword) {
      const kw = filters.keyword.toLowerCase();
      result = result.filter(v =>
        v.plateNumber.toLowerCase().includes(kw) ||
        v.company.toLowerCase().includes(kw)
      );
    }
    return result;
  },

  // 获取车辆详情
  getVehicleById: function(vehicleId) {
    return vehicles.find(v => v.id === vehicleId || v.plateNumber === vehicleId);
  },

  // 获取司机列表
  getDrivers: function(filters = {}) {
    let result = [...drivers];
    if (filters.status && filters.status !== 'all') {
      result = result.filter(d => d.status === filters.status);
    }
    if (filters.drivingLicense && filters.drivingLicense !== 'all') {
      result = result.filter(d => d.drivingLicense === filters.drivingLicense);
    }
    if (filters.keyword) {
      const kw = filters.keyword.toLowerCase();
      result = result.filter(d =>
        d.name.toLowerCase().includes(kw) ||
        d.phone.includes(kw)
      );
    }
    return result;
  },

  // 获取司机详情
  getDriverById: function(driverId) {
    return drivers.find(d => d.id === driverId);
  },

  // 获取异常列表
  getExceptions: function(filters = {}) {
    let result = [...exceptions];
    if (filters.status && filters.status !== 'all') {
      result = result.filter(e => e.status === filters.status);
    }
    if (filters.type && filters.type !== 'all') {
      result = result.filter(e => e.type === filters.type);
    }
    return result;
  },

  // 获取异常详情
  getExceptionById: function(exceptionId) {
    return exceptions.find(e => e.id === exceptionId);
  },

  // 获取轨迹数据
  getTrackByOrderId: function(orderId) {
    return trackPoints.find(t => t.orderId === orderId);
  },

  // 获取统计数据
  getStatistics: function(type) {
    if (type && statisticsData[type]) {
      return statisticsData[type];
    }
    return statisticsData;
  }
};

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MockData;
} else {
  window.MockData = MockData;
}