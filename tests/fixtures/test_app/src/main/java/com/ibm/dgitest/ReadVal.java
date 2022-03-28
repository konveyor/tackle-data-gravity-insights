package com.ibm.dgitest;

import java.util.Random;

public class ReadVal {
    int intVal;
    float floatVal;

    public ReadVal() {
    }

    public int getInt() {
        this.intVal = (new Random()).nextInt();
        return intVal;
    }

    public float getFloat() {
        this.floatVal = (new Random()).nextFloat();
        return floatVal;
    }

}
