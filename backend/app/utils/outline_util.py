import random
from typing import Dict, Tuple


def get_random_indexes(max_index: int) -> Tuple[int, int]:
    """
    从0到max_index范围内随机选择两个不同的索引
    
    Args:
        max_index: 索引的最大值（不包含）
        
    Returns:
        Tuple[int, int]: 两个不同的随机索引
    """
    if max_index < 2:
        raise ValueError("max_index must be at least 2 to select two different indexes")
    
    # 生成所有可能的索引对
    all_pairs = [(i, j) for i in range(max_index) for j in range(max_index) if i != j]
    
    # 随机选择一对索引
    selected_pair = random.choice(all_pairs)
    
    return selected_pair


def calculate_nodes_distribution(level1_count: int, important_indexes: tuple[int, int], total_leaf_nodes: int) -> dict:
    """
    计算树结构中各节点的分配数量
    
    Args:
        level1_count: 一级节点数量
        important_indexes: 两个重要节点的索引（从0开始）
        total_leaf_nodes: 需要的叶子节点总数
    
    Returns:
        dict: 包含节点分配信息的字典，格式如下：
        {
            'level2_nodes': [4, 3, 3],  # 每个一级节点下的二级节点数量
            'leaf_nodes': [12, 8, 8],   # 每个一级节点下的叶子节点数量
            'leaf_per_level2': [[3,3,3,3], [2,3,3], [3,3,2]]  # 每个二级节点下的叶子节点数量
        }
    """
    # 计算重要节点和普通节点的权重
    primary_weight = 1.4    # 第一重要节点的权重
    secondary_weight = 1.2  # 第二重要节点的权重
    normal_weight = 1.0     # 普通节点的权重
    
    # 计算总权重
    total_weight = (level1_count - 2) * normal_weight + primary_weight + secondary_weight
    
    # 计算基础二级节点数（向上取整）
    base_level2_per_node = round(total_leaf_nodes / level1_count / 3)  # 假设每个二级节点平均有3个叶子节点
    
    # 初始化结果数组
    level2_nodes = [base_level2_per_node] * level1_count
    leaf_nodes = [0] * level1_count
    
    # 为重要节点增加额外的二级节点
    level2_nodes[important_indexes[0]] = round(base_level2_per_node * primary_weight)
    level2_nodes[important_indexes[1]] = round(base_level2_per_node * secondary_weight)
    
    # 计算叶子节点分配
    remaining_leaves = total_leaf_nodes
    leaf_per_level2 = []
    
    for i in range(level1_count):
        current_level2_count = level2_nodes[i]
        
        # 计算当前一级节点应获得的叶子节点数量
        if i == important_indexes[0]:
            weight = primary_weight
        elif i == important_indexes[1]:
            weight = secondary_weight
        else:
            weight = normal_weight
            
        target_leaves = round((total_leaf_nodes * weight / total_weight))
        if i == level1_count - 1:  # 最后一个节点获得所有剩余的叶子节点
            target_leaves = remaining_leaves
            
        # 为每个二级节点分配叶子节点
        current_leaf_distribution = []
        leaves_per_level2 = target_leaves // current_level2_count
        extra_leaves = target_leaves % current_level2_count
        
        for j in range(current_level2_count):
            if j < extra_leaves:
                current_leaf_distribution.append(leaves_per_level2 + 1)
            else:
                current_leaf_distribution.append(leaves_per_level2)
        
        leaf_per_level2.append(current_leaf_distribution)
        leaf_nodes[i] = target_leaves
        remaining_leaves -= target_leaves
    
    return {
        'level2_nodes': level2_nodes,
        'leaf_nodes': leaf_nodes,
        'leaf_per_level2': leaf_per_level2
    }

def generate_one_outline_json_by_level1(level1_title: str, level1_index: int, nodes_distribution: Dict) -> Dict:
    """
    根据一级标题生成该标题下的完整大纲结构
    
    Args:
        level1_title: 一级标题
        level1_index: 一级标题的索引（从1开始）
        nodes_distribution: 节点分配信息，包含 level2_nodes 和 leaf_per_level2
        
    Returns:
        Dict: 一级标题的完整大纲结构
    """
    # 获取当前一级节点下的二级节点数量和叶子节点分配
    level2_count = nodes_distribution['level2_nodes'][level1_index - 1]
    leaf_distribution = nodes_distribution['leaf_per_level2'][level1_index - 1]
    
    # 创建一级节点
    level1_node = {
        "id":f"{level1_index}",
        "title": level1_title,
        "description": "",
        "children": []
    }
    
    # 创建二级节点
    for j in range(level2_count):
        level2_node = {
            "id":f"{level1_index}.{j+1}",
            "title": "",  # 二级标题留空
            "description": "",
            "children": []
        }
        
        # 创建三级节点（叶子节点）
        leaf_count = leaf_distribution[j]
        for k in range(leaf_count):
            level2_node["children"].append({
                "id":f"{level1_index}.{j+1}.{k+1}",
                "title": "",  # 三级标题留空
                "description": ""
            })
        
        level1_node["children"].append(level2_node)
    
    return level1_node