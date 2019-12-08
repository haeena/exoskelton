import ptvsd

from exoskelton.run import app


ptvsd.enable_attach(address=("0.0.0.0", 43443), redirect_output=True)
ptvsd.wait_for_attach()
ptvsd.break_into_debugger()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
