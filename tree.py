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

tree_save_path.write_text(tree, encoding="utf-8")

# ---

test_tree_save_path = Path(__file__).parent / "test_tree.txt"

test_tree: str = DisplayTree(
    dirPath=str(Path(__file__).parent / "tests"),
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

test_tree_save_path.write_text(test_tree, encoding="utf-8")
