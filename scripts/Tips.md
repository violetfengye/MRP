### 执行顺序：

1. **`insert_materials.py`**  
   **首先执行**：因为其他表（如 BOM、库存、调配构成等）依赖 `Material` 表的物料信息，这意味着 `Material` 数据必须先插入，以确保在后续插入过程中能够正确引用外键。

2. **`insert_inventories.py`**  
   **第二步执行**：在物料插入之后，插入库存数据。`Inventory` 模型中引用了 `Material` 表作为外键，因此需要确保 `Material` 中的数据已经存在。

3. **`insert_boms.py`**  
   **第三步执行**：接下来可以插入 BOM 数据。`BillOfMaterial` 模型中也依赖 `Material` 作为外键。

4. **`insert_allocation_compositions.py`**  
   **最后执行**：因为 `AllocationComposition` 模型中的外键（父物料、子物料）同样依赖 `Material` 表中的数据，因此它应该放在最后一步，确保所有相关物料、BOM、库存都已准备好。

### 总结：
顺序为：
1. 插入 `Material` 表中的数据（`insert_materials.py`）
2. 插入 `Inventory` 表中的数据（`insert_inventories.py`）
3. 插入 `BillOfMaterial` 表中的数据（`insert_boms.py`）
4. 插入 `AllocationComposition` 表中的数据（`insert_allocation_compositions.py`）

这样可以确保所有外键引用的数据已经在数据库中存在，避免外键约束导致的错误。