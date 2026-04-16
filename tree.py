from pathlib import Path

from directory_tree import DisplayTree

work_path = Path(__file__).parent / "src"
tree_save_path = Path(__file__).parent / "tree.txt"

tree: str = DisplayTree(
    dirPath=str(work_path),
    stringRep=True,
    header=False,
    maxDepth=float("inf"),
    showHidden=False,
    ignoreList=["__pycache__", "old", "app1.py", "example.env", "*.html"],
    onlyFiles=False,
    onlyDirs=False,
    sortBy=0,
    raiseException=False,
    printErrorTraceback=False,
)

print(tree)

tree_save_path.write_text(tree, encoding="utf-8")
