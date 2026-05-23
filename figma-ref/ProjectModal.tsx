import { X } from 'lucide-react';
import { useState, useEffect } from 'react';

interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, description: string, clientInfo: string, province: string, city: string, stage: string, industry: string) => void;
  initialName?: string;
  initialDescription?: string;
  initialClientInfo?: string;
  initialProvince?: string;
  initialCity?: string;
  initialStage?: string;
  initialIndustry?: string;
  title: string;
}

// 中国省市数据
const provincesCities: Record<string, string[]> = {
  '北京': ['东城区', '西城区', '朝阳区', '海淀区', '丰台区', '石景山区', '通州区', '顺义区', '昌平区', '大兴区', '房山区', '门头沟区', '平谷区', '密云区', '怀柔区', '延庆区'],
  '上海': ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区', '浦东新区', '闵行区', '宝山区', '嘉定区', '金山区', '松江区', '青浦区', '奉贤区', '崇明区'],
  '天津': ['和平区', '河东区', '河西区', '南开区', '河北区', '红桥区', '滨海新区', '东丽区', '西青区', '津南区', '北辰区', '武清区', '宝坻区', '宁河区', '静海区', '蓟州区'],
  '重庆': ['渝中区', '江北区', '南岸区', '九龙坡区', '沙坪坝区', '大渡口区', '渝北区', '巴南区', '北碚区', '万州区', '涪陵区', '黔江区'],
  '广东': ['广州市', '深圳市', '珠海市', '汕头市', '佛山市', '韶关市', '湛江市', '肇庆市', '江门市', '茂名市', '惠州市', '梅州市', '汕尾市', '河源市', '阳江市', '清远市', '东莞市', '中山市', '潮州市', '揭阳市', '云浮市'],
  '浙江': ['杭州市', '宁波市', '温州市', '嘉兴市', '湖州市', '绍兴市', '金华市', '衢州市', '舟山市', '台州市', '丽水市'],
  '江苏': ['南京市', '无锡市', '徐州市', '常州市', '苏州市', '南通市', '连云港市', '淮安市', '盐城市', '扬州市', '镇江市', '泰州市', '宿迁市'],
  '山东': ['济南市', '青岛市', '淄博市', '枣庄市', '东营市', '烟台市', '潍坊市', '济宁市', '泰安市', '威海市', '日照市', '临沂市', '德州市', '聊城市', '滨州市', '菏泽市'],
  '四川': ['成都市', '自贡市', '攀枝花市', '泸州市', '德阳市', '绵阳市', '广元市', '遂宁市', '内江市', '乐山市', '南充市', '眉山市', '宜宾市', '广安市', '达州市', '雅安市', '巴中市', '资阳市'],
  '河南': ['郑州市', '开封市', '洛阳市', '平顶山市', '安阳市', '鹤壁市', '新乡市', '焦作市', '濮阳市', '许昌市', '漯河市', '三门峡市', '南阳市', '商丘市', '信阳市', '周口市', '驻马店市'],
  '湖北': ['武汉市', '黄石市', '十堰市', '宜昌市', '襄阳市', '鄂州市', '荆门市', '孝感市', '荆州市', '黄冈市', '咸宁市', '随州市'],
  '湖南': ['长沙市', '株洲市', '湘潭市', '衡阳市', '邵阳市', '岳阳市', '常德市', '张家界市', '益阳市', '郴州市', '永州市', '怀化市', '娄底市'],
  '福建': ['福州市', '厦门市', '莆田市', '三明市', '泉州市', '漳州市', '南平市', '龙岩市', '宁德市'],
  '安徽': ['合肥市', '芜湖市', '蚌埠市', '淮南市', '马鞍山市', '淮北市', '铜陵市', '安庆市', '黄山市', '滁州市', '阜阳市', '宿州市', '六安市', '亳州市', '池州市', '宣城市'],
  '江西': ['南昌市', '景德镇市', '萍乡市', '九江市', '新余市', '鹰潭市', '赣州市', '吉安市', '宜春市', '抚州市', '上饶市'],
  '辽宁': ['沈阳市', '大连市', '鞍山市', '抚顺市', '本溪市', '丹东市', '锦州市', '营口市', '阜新市', '辽阳市', '盘锦市', '铁岭市', '朝阳市', '葫芦岛市'],
  '河北': ['石家庄市', '唐山市', '秦皇岛市', '邯郸市', '邢台市', '保定市', '张家口市', '承德市', '沧州市', '廊坊市', '衡水市'],
  '陕西': ['西安市', '铜川市', '宝鸡市', '咸阳市', '渭南市', '延安市', '汉中市', '榆林市', '安康市', '商洛市'],
  '山西': ['太原市', '大同市', '阳泉市', '长治市', '晋城市', '朔州市', '晋中市', '运城市', '忻州市', '临汾市', '吕梁市'],
  '黑龙江': ['哈尔滨市', '齐齐哈尔市', '鸡西市', '鹤岗市', '双鸭山市', '大庆市', '伊春市', '佳木斯市', '七台河市', '牡丹江市', '黑河市', '绥化市'],
  '吉林': ['长春市', '吉林市', '四平市', '辽源市', '通化市', '白山市', '松原市', '白城市'],
  '云南': ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市'],
  '贵州': ['贵阳市', '六盘水市', '遵义市', '安顺市', '毕节市', '铜仁市'],
  '甘肃': ['兰州市', '嘉峪关市', '金昌市', '白银市', '天水市', '武威市', '张掖市', '平凉市', '酒泉市', '庆阳市', '定西市', '陇南市'],
  '广西': ['南宁市', '柳州市', '桂林市', '梧州市', '北海市', '防城港市', '钦州市', '贵港市', '玉林市', '百色市', '贺州市', '河池市', '来宾市', '崇左市'],
  '内蒙古': ['呼和浩特市', '包头市', '乌海市', '赤峰市', '通辽市', '鄂尔多斯市', '呼伦贝尔市', '巴彦淖尔市', '乌兰察布市'],
  '新疆': ['乌鲁木齐市', '克拉玛依市', '吐鲁番市', '哈密市', '昌吉回族自治州', '博尔塔拉蒙古自治州', '巴音郭楞蒙古自治州', '阿克苏地区', '喀什地区', '和田地区'],
  '宁夏': ['银川市', '石嘴山市', '吴忠市', '固原市', '中卫市'],
  '青海': ['西宁市', '海东市'],
  '西藏': ['拉萨市', '日喀则市', '昌都市', '林芝市', '山南市', '那曲市'],
  '海南': ['海口市', '三亚市', '三沙市', '儋州市']
};

export function ProjectModal({ isOpen, onClose, onSave, initialName = '', initialDescription = '', initialClientInfo = '', initialProvince = '', initialCity = '', initialStage = '', initialIndustry = '', title }: ProjectModalProps) {
  const [name, setName] = useState(initialName);
  const [description, setDescription] = useState(initialDescription);
  const [clientInfo, setClientInfo] = useState(initialClientInfo);
  const [province, setProvince] = useState(initialProvince);
  const [city, setCity] = useState(initialCity);
  const [stage, setStage] = useState(initialStage);
  const [industry, setIndustry] = useState(initialIndustry);
  const [isClosing, setIsClosing] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsClosing(false);
      setName(initialName);
      setDescription(initialDescription);
      setClientInfo(initialClientInfo);
      setProvince(initialProvince);
      setCity(initialCity);
      setStage(initialStage);
      setIndustry(initialIndustry);
    }
  }, [isOpen, initialName, initialDescription, initialClientInfo, initialProvince, initialCity, initialStage, initialIndustry]);

  useEffect(() => {
    if (!isOpen) {
      // 在modal关闭动画完成后再清空字段
      const timer = setTimeout(() => {
        setName('');
        setDescription('');
        setClientInfo('');
        setProvince('');
        setCity('');
        setStage('');
        setIndustry('');
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim() && clientInfo.trim() && province && city && stage && industry) {
      onSave(name.trim(), description.trim(), clientInfo.trim(), province, city, stage, industry);
      setIsClosing(true);
      setTimeout(() => {
        onClose();
        setIsClosing(false);
      }, 200);
    }
  };

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      onClose();
      setIsClosing(false);
    }, 200);
  };

  const handleProvinceChange = (selectedProvince: string) => {
    setProvince(selectedProvince);
    setCity(''); // 重置城市选择
  };

  return (
    <div
      className={`fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-200 ${isClosing ? 'opacity-0' : 'opacity-100'}`}
      onClick={handleClose}
    >
      <div
        className={`bg-white rounded-2xl p-8 w-full max-w-lg shadow-2xl border border-slate-200 max-h-[90vh] overflow-y-auto transition-all duration-200 ${isClosing ? 'scale-95 opacity-0' : 'scale-100 opacity-100'}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-slate-900">{title}</h2>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            aria-label="关闭"
          >
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-5">
            <label htmlFor="project-name" className="block mb-2 text-sm font-medium text-slate-700">
              项目名称 <span className="text-red-500">*</span>
            </label>
            <input
              id="project-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="输入项目名称"
              autoFocus
              required
            />
          </div>

          <div className="mb-5">
            <label htmlFor="client-info" className="block mb-2 text-sm font-medium text-slate-700">
              客户信息 <span className="text-red-500">*</span>
            </label>
            <input
              id="client-info"
              type="text"
              value={clientInfo}
              onChange={(e) => setClientInfo(e.target.value)}
              className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              placeholder="输入客户名称或公司"
              required
            />
          </div>

          <div className="mb-5">
            <label htmlFor="project-description" className="block mb-2 text-sm font-medium text-slate-700">
              项目描述
            </label>
            <textarea
              id="project-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all"
              placeholder="输入项目描述（可选）"
              rows={3}
            />
          </div>

          <div className="mb-5">
            <label className="block mb-2 text-sm font-medium text-slate-700">
              项目区域 <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <select
                  value={province}
                  onChange={(e) => handleProvinceChange(e.target.value)}
                  className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                >
                  <option value="">请选择省份</option>
                  {Object.keys(provincesCities).map((prov) => (
                    <option key={prov} value={prov}>
                      {prov}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <select
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:bg-slate-50 disabled:cursor-not-allowed"
                  disabled={!province}
                  required
                >
                  <option value="">请选择城市</option>
                  {province && provincesCities[province]?.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="mb-5">
            <label htmlFor="project-stage" className="block mb-2 text-sm font-medium text-slate-700">
              项目阶段 <span className="text-red-500">*</span>
            </label>
            <select
              id="project-stage"
              value={stage}
              onChange={(e) => setStage(e.target.value)}
              className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              required
            >
              <option value="">请选择项目阶段</option>
              <option value="情报收集">情报收集</option>
              <option value="需求阶段">需求阶段</option>
              <option value="需求分析">需求分析</option>
              <option value="方案设计">方案设计</option>
              <option value="报价阶段">报价阶段</option>
              <option value="项目立项">项目立项</option>
            </select>
          </div>

          <div className="mb-6">
            <label htmlFor="project-industry" className="block mb-2 text-sm font-medium text-slate-700">
              项目归属行业 <span className="text-red-500">*</span>
            </label>
            <select
              id="project-industry"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full px-4 py-3 bg-white border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              required
            >
              <option value="">请选择归属行业</option>
              <option value="物流/仓储">物流/仓储</option>
              <option value="教育">教育</option>
              <option value="医疗健康">医疗健康</option>
              <option value="金融">金融</option>
              <option value="制造业">制造业</option>
              <option value="零售/电商">零售/电商</option>
              <option value="政府/公共服务">政府/公共服务</option>
              <option value="能源/环保">能源/环保</option>
              <option value="交通运输">交通运输</option>
              <option value="房地产/建筑">房地产/建筑</option>
              <option value="互联网/科技">互联网/科技</option>
              <option value="农业">农业</option>
              <option value="文化/娱乐">文化/娱乐</option>
              <option value="其他">其他</option>
            </select>
          </div>

          <div className="flex gap-3 justify-end pt-4 border-t border-slate-200">
            <button
              type="button"
              onClick={handleClose}
              className="px-6 py-2.5 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-colors font-medium"
            >
              取消
            </button>
            <button
              type="submit"
              className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg shadow-blue-500/30 font-medium"
            >
              保存项目
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
