package com.ibm.dgitest;

import java.util.List;
import java.util.ArrayList;

public class DGIMain {
    public static void main(String... args) {
        List<Obj> objList = new ArrayList<>();

        Obj o1 = new Obj(); // Obj/1
        Obj o2 = new Obj(); // Obj/2
        objList.add(o1);
        objList.add(o2);

        input(objList);
        int x = objList.get(0).getX();
        int y = objList.get(1).getY();
        int r = add(x, y);
        System.out.println(r);
    }

    public static void input(List<Obj> arr) {
        ReadVal read = new ReadVal();
        int x_0 = read.getInt();
        int y_0 = read.getInt();
        int x_1 = read.getInt();
        int y_1 = read.getInt();

        arr.get(0).setX(x_0);
        arr.get(0).setY(y_0);
        arr.get(1).setX(x_1);
        arr.get(1).setY(y_1);

    }

    public static int add(int x, int y) {
        int r = x + y;
        return r;
    }
}