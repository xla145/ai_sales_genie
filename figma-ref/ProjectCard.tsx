import { Pencil, Trash2, FolderOpen, Building2, MapPin } from 'lucide-react';
import { motion } from 'motion/react';

interface ProjectCardProps {
  id: string;
  name: string;
  description: string;
  clientInfo: string;
  province: string;
  city: string;
  createdAt: string;
  onEdit: () => void;
  onDelete: () => void;
  onEnter: () => void;
  isNew?: boolean;
  isFading?: boolean;
}

export function ProjectCard({ name, description, clientInfo, province, city, createdAt, onEdit, onDelete, onEnter, isNew, isFading }: ProjectCardProps) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ duration: 0.2 }}
      className={`group relative bg-white border border-slate-200/50 rounded-2xl p-5 shadow-sm hover:shadow-xl hover:shadow-blue-500/10 transition-all duration-300 overflow-hidden ${
        isFading
          ? 'opacity-0 scale-95'
          : isNew
            ? 'animate-[slideIn_0.4s_ease-out]'
            : ''
      }`}
    >
      {/* 背景渐变效果 */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-50 to-transparent rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10" />

      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-slate-900 mb-2 truncate group-hover:text-blue-600 transition-colors">{name}</h3>
          <p className="text-sm text-slate-600 line-clamp-2 mb-3 leading-relaxed">{description || '暂无描述'}</p>
          <div className="flex flex-wrap gap-2 text-xs">
            {clientInfo && (
              <div className="flex items-center gap-1.5 text-slate-700 bg-gradient-to-br from-blue-50 to-blue-100/50 px-2.5 py-1.5 rounded-lg border border-blue-100">
                <Building2 className="w-3.5 h-3.5 text-blue-600" />
                <span className="font-medium">{clientInfo}</span>
              </div>
            )}
            {(province || city) && (
              <div className="flex items-center gap-1.5 text-slate-700 bg-slate-50 px-2.5 py-1.5 rounded-lg border border-slate-100">
                <MapPin className="w-3.5 h-3.5 text-slate-500" />
                <span>{[province, city].filter(Boolean).join(' · ')}</span>
              </div>
            )}
          </div>
        </div>
        <div className="flex gap-1.5 ml-3">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={onEdit}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            aria-label="编辑项目"
          >
            <Pencil className="w-4 h-4 text-slate-400 hover:text-slate-700" />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={onDelete}
            className="p-2 hover:bg-red-50 rounded-lg transition-colors"
            aria-label="删除项目"
          >
            <Trash2 className="w-4 h-4 text-slate-400 hover:text-red-600" />
          </motion.button>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
        <span className="text-xs text-slate-500 font-medium">
          {new Date(createdAt).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })}
        </span>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onEnter}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl text-xs font-medium hover:shadow-md hover:shadow-blue-500/30 transition-all"
        >
          <FolderOpen className="w-3.5 h-3.5" />
          进入项目
        </motion.button>
      </div>
    </motion.div>
  );
}
