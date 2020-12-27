package net.gree_advertising.uranow.adapter

import android.support.v7.util.SortedList
import android.support.v7.widget.RecyclerView

abstract class SortedRecyclerViewAdapter<T, VH>
    : RecyclerView.Adapter<VH>() where VH: RecyclerView.ViewHolder {

    abstract var sortedList: SortedList<T>

    override fun getItemCount(): Int {
        return sortedList.size()
    }

    fun addItems(items :List<T>) {
        sortedList.addAll(items)
    }
}
