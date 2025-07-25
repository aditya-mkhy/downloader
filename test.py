def m():
    n = "d"
    global k

    k = 20

    try:
        print("Try is running...")
        k = 30
        n = n / 10

    except Exception as e:
        print(f"Exception occur {e}")
        return "hello  i returned from ex"


    finally:
        print("i am finally")
        


k = 10
s = m()
print("return : ", s)
print("vlue of k => ", k)
