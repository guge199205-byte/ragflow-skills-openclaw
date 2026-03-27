#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAGFlow 基础使用示例

演示最常用的 API 调用
"""

from python.client import RAGFlow


def main():
    # 1. 初始化客户端
    print("=" * 60)
    print("RAGFlow 基础使用示例")
    print("=" * 60)
    
    client = RAGFlow.from_env()
    
    # 2. 测试连接
    print("\n1️⃣ 测试连接...")
    result = client.test_connection()
    if result['status'] == 'success':
        print(f"✅ 连接成功！知识库数量：{result['kb_count']}")
    else:
        print(f"❌ 连接失败：{result['message']}")
        return
    
    # 3. 列出知识库
    print("\n2️⃣ 知识库列表:")
    kbs = client.list_knowledge_bases()
    for i, kb in enumerate(kbs, 1):
        print(f"   {i}. {kb.name}")
        print(f"      文档：{kb.document_count}, Chunk: {kb.chunk_count}")
    
    # 4. 创建知识库（如果数量<3）
    if len(kbs) < 3:
        print("\n3️⃣ 创建测试知识库...")
        kb = client.create_knowledge_base(
            name="测试知识库",
            description="用于测试的知识库"
        )
        print(f"✅ 创建成功！ID: {kb.id}")
    
    # 5. 查询知识库
    print("\n4️⃣ 查询知识库...")
    if kbs:
        query = "润滑脂的主要成分"
        print(f"   问题：{query}")
        
        try:
            result = client.query(query, kb_ids=[kbs[0].id])
            print(f"   答案：{result.answer}")
            
            if result.references:
                print(f"\n   参考资料 ({len(result.references)} 条):")
                for ref in result.references[:3]:  # 显示前 3 条
                    print(f"   - {ref.document_name}")
                    print(f"     {ref.content[:100]}...")
        except Exception as e:
            print(f"   ⚠️ 查询失败：{e}")
            print("   提示：需要先上传并解析文档")
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
