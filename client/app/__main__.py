from asyncio import run
from app.main import main
import traceback

if __name__ == '__main__':
    run(main())
    traceback.print_exc()
